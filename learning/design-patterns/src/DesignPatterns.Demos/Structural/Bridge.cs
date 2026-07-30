namespace DesignPatterns.Demos.Structural.Bridge;

/// <summary>
/// BRIDGE — tách 1 abstraction (VD: loại thiết bị) khỏi implementation (VD: cách điều khiển) thành
/// 2 hệ phân cấp độc lập, nối với nhau bằng tham chiếu — tránh bùng nổ tổ hợp lớp con (M loại x N cách).
/// Khi nào dùng: có 2 chiều biến đổi độc lập cùng lúc (loại thiết bị × giao thức điều khiển).
/// Khi KHÔNG nên dùng: chỉ có 1 chiều biến đổi — kế thừa thường (không cần bridge) là đủ.
/// </summary>
public interface IRemoteControlProtocol
{
    void SendPowerSignal(bool on);
    void SendVolumeSignal(int delta);
}

public class InfraredProtocol : IRemoteControlProtocol
{
    public void SendPowerSignal(bool on) => Console.WriteLine($"[Hồng ngoại] gửi tín hiệu power={on}");
    public void SendVolumeSignal(int delta) => Console.WriteLine($"[Hồng ngoại] gửi tín hiệu volume {delta:+0;-0}");
}

public class BluetoothProtocol : IRemoteControlProtocol
{
    public void SendPowerSignal(bool on) => Console.WriteLine($"[Bluetooth] gửi packet power={on}");
    public void SendVolumeSignal(int delta) => Console.WriteLine($"[Bluetooth] gửi packet volume {delta:+0;-0}");
}

// Abstraction — không quan tâm giao thức cụ thể, chỉ giữ tham chiếu (cầu nối) tới nó.
public abstract class RemoteControl
{
    protected readonly IRemoteControlProtocol Protocol;
    protected RemoteControl(IRemoteControlProtocol protocol) => Protocol = protocol;

    public abstract void TogglePower();
}

public class BasicRemoteControl : RemoteControl
{
    private bool _isOn;
    public BasicRemoteControl(IRemoteControlProtocol protocol) : base(protocol) { }
    public override void TogglePower() { _isOn = !_isOn; Protocol.SendPowerSignal(_isOn); }
}

public class SmartRemoteControl : RemoteControl
{
    private bool _isOn;
    public SmartRemoteControl(IRemoteControlProtocol protocol) : base(protocol) { }
    public override void TogglePower() { _isOn = !_isOn; Protocol.SendPowerSignal(_isOn); }
    public void VolumeUp() => Protocol.SendVolumeSignal(+1);
}

public class BridgeDemo : IPatternDemo
{
    public string Category => "Structural";
    public string Name => "Bridge";

    public void Run()
    {
        // 2 loại remote × 2 giao thức = 4 tổ hợp, nhưng chỉ cần 2+2 = 4 class thay vì viết riêng 4 class lai.
        new BasicRemoteControl(new InfraredProtocol()).TogglePower();
        new SmartRemoteControl(new BluetoothProtocol()).TogglePower();
    }
}
