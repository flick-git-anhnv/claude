#!/bin/bash
# Cài SQL Server Express trên Ubuntu 22.04 + (tuỳ chọn) restore DB từ file backup .bak
# Dùng chung cho mọi project cần deploy SQL Server trên Ubuntu (VM/kiosk/server thật).
#
# Chỉnh 4 biến bên dưới cho đúng project trước khi chạy, rồi:
#   chmod +x setup-mssql-server.sh && ./setup-mssql-server.sh
set -e

SA_PASSWORD="Kztek123456"                     # đổi mật khẩu SA tại đây trước khi chạy
DB_NAME="IPGS2023"                            # tên database cần restore (để trống "" nếu chỉ cần cài đặt, không restore)
BACKUP_PATH="$HOME/Documents/ccu/pgs.bak"     # đường dẫn file .bak copy thủ công vào máy này
BACKUP_DEST="/var/opt/mssql/backup/pgs.bak"   # đường dẫn SQL Server sẽ đọc file backup

echo "=== [1/7] Dọn dẹp cấu hình cũ (nếu có) ==="
sudo apt-get remove --purge -y mssql-server 2>/dev/null || true
sudo rm -f /usr/share/keyrings/microsoft-prod.gpg
sudo rm -f /etc/apt/sources.list.d/mssql-server.list
sudo rm -f /etc/apt/sources.list.d/mssql-release.list
sudo dpkg --configure -a

echo "=== [2/7] Import GPG key + repo (kèm signed-by, tránh lỗi NO_PUBKEY) ==="
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc -o /tmp/microsoft.asc
sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg /tmp/microsoft.asc
echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/22.04/mssql-server-2022 jammy main" | sudo tee /etc/apt/sources.list.d/mssql-server.list
sudo apt-get update

echo "=== [3/7] Cài SQL Server ==="
sudo apt-get install -y mssql-server

echo "=== [4/7] Cấu hình non-interactive (Express edition) ==="
sudo MSSQL_PID=Express ACCEPT_EULA=Y MSSQL_SA_PASSWORD="$SA_PASSWORD" /opt/mssql/bin/mssql-conf -n setup

echo "=== [5/7] Mở firewall + kiểm tra service ==="
sudo ufw allow 1433/tcp || true
sleep 5
systemctl is-active --quiet mssql-server && echo "mssql-server: RUNNING" || { echo "mssql-server: NOT RUNNING - kiểm tra: sudo journalctl -u mssql-server --no-pager | tail -50"; exit 1; }

echo "=== [6/7] Cài sqlcmd (mssql-tools18) ==="
if [ ! -f /opt/mssql-tools18/bin/sqlcmd ]; then
    echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" | sudo tee /etc/apt/sources.list.d/mssql-release.list
    sudo apt-get update
    sudo ACCEPT_EULA=Y apt-get install -y mssql-tools18 unixodbc-dev
fi
export PATH="$PATH:/opt/mssql-tools18/bin"
grep -qxF 'export PATH="$PATH:/opt/mssql-tools18/bin"' ~/.bashrc || echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc

echo "=== Test kết nối SQL Server ==="
sqlcmd -S localhost -U SA -P "$SA_PASSWORD" -No -Q "SELECT @@VERSION"

if [ -z "$DB_NAME" ]; then
    echo "=== DB_NAME để trống — bỏ qua bước restore ==="
    echo "=== HOÀN TẤT (chỉ cài đặt) ==="
    exit 0
fi

echo "=== [7/7] Restore DB $DB_NAME từ $BACKUP_PATH (nếu file đã copy vào) ==="
if [ -f "$BACKUP_PATH" ]; then
    sudo mkdir -p /var/opt/mssql/backup
    sudo cp "$BACKUP_PATH" "$BACKUP_DEST"
    sudo chown mssql:mssql "$BACKUP_DEST"

    cat > /tmp/filelist.sql <<SQL
SET NOCOUNT ON;
CREATE TABLE #f (
    LogicalName nvarchar(128), PhysicalName nvarchar(260), Type char(1),
    FileGroupName nvarchar(128), Size numeric(20,0), MaxSize numeric(20,0),
    FileId bigint, CreateLSN numeric(25,0), DropLSN numeric(25,0),
    UniqueId uniqueidentifier, ReadOnlyLSN numeric(25,0), ReadWriteLSN numeric(25,0),
    BackupSizeInBytes bigint, SourceBlockSize int, FileGroupId int,
    LogGroupGUID uniqueidentifier, DifferentialBaseLSN numeric(25,0),
    DifferentialBaseGUID uniqueidentifier, IsReadOnly bit, IsPresent bit,
    TDEThumbprint varbinary(32), SnapshotUrl nvarchar(360)
);
INSERT INTO #f EXEC('RESTORE FILELISTONLY FROM DISK = ''$BACKUP_DEST''');
SELECT LogicalName, Type FROM #f;
SQL

    echo "--- Danh sách logical file trong bản backup ---"
    sqlcmd -S localhost -U SA -P "$SA_PASSWORD" -No -h -1 -W -s"|" -i /tmp/filelist.sql -o /tmp/filelist.csv
    cat /tmp/filelist.csv

    MDF_LOGICAL=$(awk -F'|' '$2=="D"{print $1; exit}' /tmp/filelist.csv | xargs)
    LDF_LOGICAL=$(awk -F'|' '$2=="L"{print $1; exit}' /tmp/filelist.csv | xargs)

    if [ -z "$MDF_LOGICAL" ] || [ -z "$LDF_LOGICAL" ]; then
        echo "Không tự xác định được logical file name — mở /tmp/filelist.csv để tự điền tay vào lệnh RESTORE."
        exit 1
    fi

    echo "MDF logical: $MDF_LOGICAL | LDF logical: $LDF_LOGICAL"

    sqlcmd -S localhost -U SA -P "$SA_PASSWORD" -No -Q "
    RESTORE DATABASE [$DB_NAME]
    FROM DISK = '$BACKUP_DEST'
    WITH MOVE '$MDF_LOGICAL' TO '/var/opt/mssql/data/${DB_NAME}.mdf',
         MOVE '$LDF_LOGICAL' TO '/var/opt/mssql/data/${DB_NAME}_log.ldf'"

    echo "--- Xác nhận trạng thái DB ---"
    sqlcmd -S localhost -U SA -P "$SA_PASSWORD" -No -Q "SELECT name, state_desc FROM sys.databases WHERE name = '$DB_NAME'"
else
    echo "Chưa thấy file backup tại $BACKUP_PATH."
    echo "Copy file .bak vào đường dẫn đó rồi chạy lại script này (các bước cài đặt đã xong sẽ tự bỏ qua nếu đã tồn tại)."
fi

echo "=== HOÀN TẤT ==="
