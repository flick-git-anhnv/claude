namespace DesignPatterns.Demos.Creational.Builder;

/// <summary>
/// BUILDER — tách quá trình xây dựng 1 object phức tạp (nhiều bước, nhiều tham số tuỳ chọn) ra khỏi
/// chính object đó, cho phép tạo từng bước và tái sử dụng cùng 1 quy trình cho nhiều đại diện khác nhau.
/// Khi nào dùng: object có quá nhiều tham số tuỳ chọn (constructor telescoping problem).
/// Khi KHÔNG nên dùng: object đơn giản, ít tham số — dùng constructor hoặc object initializer là đủ.
/// </summary>
public class HttpRequest
{
    public string Url { get; init; } = "";
    public string Method { get; init; } = "GET";
    public Dictionary<string, string> Headers { get; init; } = new();
    public string? Body { get; init; }

    public override string ToString() =>
        $"{Method} {Url}\nHeaders: {string.Join(", ", Headers.Select(h => $"{h.Key}={h.Value}"))}\nBody: {Body ?? "(none)"}";
}

public class HttpRequestBuilder
{
    private string _url = "";
    private string _method = "GET";
    private readonly Dictionary<string, string> _headers = new();
    private string? _body;

    public HttpRequestBuilder WithUrl(string url) { _url = url; return this; }
    public HttpRequestBuilder WithMethod(string method) { _method = method; return this; }
    public HttpRequestBuilder WithHeader(string key, string value) { _headers[key] = value; return this; }
    public HttpRequestBuilder WithBody(string body) { _body = body; return this; }

    public HttpRequest Build() => new()
    {
        Url = _url,
        Method = _method,
        Headers = _headers,
        Body = _body
    };
}

public class BuilderDemo : IPatternDemo
{
    public string Category => "Creational";
    public string Name => "Builder";

    public void Run()
    {
        var request = new HttpRequestBuilder()
            .WithUrl("https://api.example.com/orders")
            .WithMethod("POST")
            .WithHeader("Content-Type", "application/json")
            .WithHeader("Authorization", "Bearer token123")
            .WithBody("{\"orderId\": 42}")
            .Build();

        Console.WriteLine(request);
    }
}
