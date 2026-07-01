using System.Collections.Generic;
using System.Text;

namespace KztekComponent.Controls
{
    /// <summary>
    /// Telex Vietnamese input method engine (stateless, call per keystroke).
    ///
    /// Vowel modifications:
    ///   aa→â  aw→ă  ee→ê  oo→ô  ow→ơ  uw→ư  dd→đ  w(alone)→ư
    ///   Second trigger on same modification = escape back to plain form.
    ///
    /// Tone keys (s/f/r/x/j/z — sắc/huyền/hỏi/ngã/nặng/xóa):
    ///   Placement follows UniKey phonological rules:
    ///   • 1 vowel in cluster                  → that vowel
    ///   • 3+ vowels in cluster                → middle vowel (index 1)
    ///   • 2 vowels, cluster ends in i/y/u     → FIRST vowel  (ai,ôi,âu,iu,ưi…)
    ///   • 2 vowels, cluster is ia/ua/ưa       → FIRST vowel  (open diphthong)
    ///   • All other 2-vowel clusters          → LAST vowel   (oa,iê,uô,ươ,oe…)
    ///   Consonant glides skipped from cluster head:
    ///     'qu' → u after q is onset glide (not a vowel of the cluster)
    ///     'gi' → i after g is onset glide
    /// </summary>
    internal static class KzTelexEngine
    {
        // ── Vowel tone table ──────────────────────────────────────────────────
        // Index 0=level 1=sắc(s) 2=huyền(f) 3=hỏi(r) 4=ngã(x) 5=nặng(j)
        private static readonly Dictionary<char, char[]> _toneTable = new Dictionary<char, char[]>
        {
            ['a'] = new[] { 'a', 'á', 'à', 'ả', 'ã', 'ạ' },
            ['ă'] = new[] { 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ' },
            ['â'] = new[] { 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ' },
            ['e'] = new[] { 'e', 'é', 'è', 'ẻ', 'ẽ', 'ẹ' },
            ['ê'] = new[] { 'ê', 'ế', 'ề', 'ể', 'ễ', 'ệ' },
            ['i'] = new[] { 'i', 'í', 'ì', 'ỉ', 'ĩ', 'ị' },
            ['o'] = new[] { 'o', 'ó', 'ò', 'ỏ', 'õ', 'ọ' },
            ['ô'] = new[] { 'ô', 'ố', 'ồ', 'ổ', 'ỗ', 'ộ' },
            ['ơ'] = new[] { 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ' },
            ['u'] = new[] { 'u', 'ú', 'ù', 'ủ', 'ũ', 'ụ' },
            ['ư'] = new[] { 'ư', 'ứ', 'ừ', 'ử', 'ữ', 'ự' },
            ['y'] = new[] { 'y', 'ý', 'ỳ', 'ỷ', 'ỹ', 'ỵ' },
        };

        // Reverse: any Vietnamese vowel char → (base vowel, tone index)
        private static readonly Dictionary<char, (char Base, int Tone)> _reverse;

        // Tone key → tone index
        private static readonly Dictionary<char, int> _toneKeys = new Dictionary<char, int>
        {
            ['s'] = 1, ['f'] = 2, ['r'] = 3, ['x'] = 4, ['j'] = 5, ['z'] = 0,
        };

        static KzTelexEngine()
        {
            _reverse = new Dictionary<char, (char, int)>();
            foreach (var kv in _toneTable)
                for (int i = 0; i < kv.Value.Length; i++)
                    _reverse[kv.Value[i]] = (kv.Key, i);
        }

        // ── Public entry point ────────────────────────────────────────────────

        /// <summary>
        /// Process one character typed on the virtual keyboard.
        /// Returns (deleteBack, insertText):
        ///   — deleteBack: how many chars to erase BEFORE the cursor
        ///   — insertText: string to insert at the cursor position
        /// If no transformation matches, returns (0, typed.ToString()).
        /// </summary>
        public static (int DeleteBack, string Insert) Process(string textBeforeCursor, char typed)
        {
            char lower  = char.ToLowerInvariant(typed);
            bool isUpper = char.IsUpper(typed);

            string word = ExtractWord(textBeforeCursor);

            // ── dd → đ ───────────────────────────────────────────────────────
            if (lower == 'd' && word.Length > 0)
            {
                char prev = word[word.Length - 1];
                if (char.ToLowerInvariant(prev) == 'd')
                    return (1, char.IsUpper(prev) ? "Đ" : "đ");
            }

            // ── vowel modification (including escape) ─────────────────────────
            if (word.Length > 0)
            {
                char prev    = word[word.Length - 1];
                char prevLow = char.ToLowerInvariant(prev);
                GetVowelInfo(prevLow, out char prevBase, out int prevTone);

                string mod = VowelMod(lower, prevBase);
                if (mod != null)
                {
                    if (mod.Length == 1)
                    {
                        // Re-apply the same tone on the new base vowel
                        char newV = ApplyTone(mod[0], prevTone);
                        string ins = char.IsUpper(prev)
                            ? char.ToUpperInvariant(newV).ToString()
                            : newV.ToString();
                        return (1, ins);
                    }
                    // Multi-char escape (e.g., "aa", "aw") — insert literally
                    return (1, mod);
                }
            }

            // ── standalone w → ư ─────────────────────────────────────────────
            if (lower == 'w')
                return (0, isUpper ? "Ư" : "ư");

            // ── tone keys: s f r x j z ────────────────────────────────────────
            if (_toneKeys.TryGetValue(lower, out int toneIdx))
            {
                int pos = FindTonePos(word);
                if (pos >= 0)
                {
                    char vc  = word[pos];
                    char vcl = char.ToLowerInvariant(vc);
                    GetVowelInfo(vcl, out char vBase, out int vTone);

                    // Toggle: pressing same tone key again removes the tone
                    int newTone = (vTone == toneIdx) ? 0 : toneIdx;
                    char newV   = ApplyTone(vBase, newTone);

                    if (newV != vcl)
                    {
                        int   del    = word.Length - pos;
                        string suffix = word.Substring(pos + 1);
                        string vStr   = char.IsUpper(vc)
                            ? char.ToUpperInvariant(newV).ToString()
                            : newV.ToString();
                        return (del, vStr + suffix);
                    }
                }
                // No suitable vowel → insert the tone key as a literal letter
            }

            // ── default: insert literal ───────────────────────────────────────
            return (0, typed.ToString());
        }

        // ── Private helpers ───────────────────────────────────────────────────

        private static void GetVowelInfo(char lowered, out char baseVowel, out int toneIdx)
        {
            if (_reverse.TryGetValue(lowered, out var info)) { baseVowel = info.Base; toneIdx = info.Tone; return; }
            baseVowel = lowered; toneIdx = 0;
        }

        private static char ApplyTone(char baseVowel, int toneIdx)
        {
            if (_toneTable.TryGetValue(baseVowel, out var arr) && (uint)toneIdx < (uint)arr.Length)
                return arr[toneIdx];
            return baseVowel;
        }

        // Vowel composition/escape rules.
        // Returns the new base vowel char (string len=1) or an escape sequence (len>1), or null.
        private static string VowelMod(char trigger, char prevBase)
        {
            switch (trigger)
            {
                case 'a':
                    if (prevBase == 'a') return "â";
                    if (prevBase == 'â') return "a";   // escape
                    if (prevBase == 'ă') return "a";   // escape
                    break;
                case 'w':
                    if (prevBase == 'a') return "ă";
                    if (prevBase == 'o') return "ơ";
                    if (prevBase == 'u') return "ư";
                    if (prevBase == 'ă') return "a";   // escape
                    if (prevBase == 'ơ') return "o";   // escape
                    if (prevBase == 'ư') return "u";   // escape
                    break;
                case 'e':
                    if (prevBase == 'e') return "ê";
                    if (prevBase == 'ê') return "e";   // escape
                    break;
                case 'o':
                    if (prevBase == 'o') return "ô";
                    if (prevBase == 'ô') return "o";   // escape
                    break;
            }
            return null;
        }

        // Returns true for any Vietnamese vowel character (base or toned).
        private static bool IsViVowel(char c) => _reverse.ContainsKey(char.ToLowerInvariant(c));

        /// <summary>
        /// Find the index in <paramref name="word"/> where a tone mark should be placed,
        /// implementing UniKey-compatible phonological cluster rules.
        /// </summary>
        private static int FindTonePos(string word)
        {
            if (string.IsNullOrEmpty(word)) return -1;

            // 1. Find the rightmost vowel — this is the end of the vowel cluster.
            //    Everything to its right is trailing consonant(s).
            int clusterEnd = -1;
            for (int i = word.Length - 1; i >= 0; i--)
            {
                if (IsViVowel(word[i])) { clusterEnd = i; break; }
            }
            if (clusterEnd < 0) return -1;

            // 2. Walk leftward collecting contiguous vowels → cluster start.
            int clusterStart = clusterEnd;
            while (clusterStart > 0 && IsViVowel(word[clusterStart - 1]))
                clusterStart--;

            // 3. Skip onset consonant glides at the cluster head:
            //      "qu"  →  the 'u' immediately after 'q' is /w/, not a vowel nucleus
            //      "gi"  →  the 'i' immediately after 'g' is /j/, not a vowel nucleus
            if (clusterStart > 0)
            {
                char preceding = char.ToLowerInvariant(word[clusterStart - 1]);
                GetVowelInfo(char.ToLowerInvariant(word[clusterStart]), out char headBase, out _);

                if ((preceding == 'q' && headBase == 'u') ||
                    (preceding == 'g' && headBase == 'i'))
                {
                    clusterStart++;
                }
            }

            int len = clusterEnd - clusterStart + 1;
            if (len <= 0) return clusterEnd; // safety: fall back to last vowel

            // 4. Apply placement rules.
            if (len == 1) return clusterStart;

            // 3+ vowels → middle (index 1 within the cluster)
            if (len >= 3) return clusterStart + 1;

            // Exactly 2 vowels — phonological rules:
            GetVowelInfo(char.ToLowerInvariant(word[clusterEnd]),   out char lastBase,  out _);
            GetVowelInfo(char.ToLowerInvariant(word[clusterStart]), out char startBase, out _);

            // Rule A: coda semi-vowel (i / y / u at end) → tone on FIRST
            //   Examples: ai, ay, âu, ôi, ơi, ui, ưi, iu, êu, uy …
            if (lastBase == 'i' || lastBase == 'y' || lastBase == 'u')
                return clusterStart;

            // Rule B: open diphthong  ia / ua / ưa → tone on FIRST (the nuclear vowel)
            //   Examples: "bìa", "múa", "mửa" — the 'a' is a trailing glide, not the nucleus
            if (lastBase == 'a' && (startBase == 'i' || startBase == 'u' || startBase == 'ư'))
                return clusterStart;

            // Rule C: everything else (oa, oe, iê, uô, ươ, …) → tone on LAST
            return clusterEnd;
        }

        // Extract the "current word" — characters immediately before the cursor,
        // stopping at the first whitespace or sentence-ending punctuation.
        private static string ExtractWord(string text)
        {
            if (string.IsNullOrEmpty(text)) return "";
            var sb = new StringBuilder();
            for (int i = text.Length - 1; i >= 0; i--)
            {
                char c = text[i];
                if (c == ' ' || c == '\n' || c == '\r' || c == '\t' ||
                    c == ',' || c == '.' || c == '?' || c == '!' ||
                    c == ':' || c == ';' || c == '(' || c == ')' ||
                    c == '[' || c == ']' || c == '"' || c == '\'')
                    break;
                sb.Insert(0, c);
            }
            return sb.ToString();
        }
    }
}
