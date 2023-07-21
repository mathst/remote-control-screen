'''
constructor TThread_Connection_Main.Create(aSocket: TCustomWinSocket);
begin
  inherited Create(False);
  Socket := aSocket;
  FreeOnTerminate := true;
end;

constructor TThread_Connection_Desktop.Create(aSocket: TCustomWinSocket);
begin
  inherited Create(False);
  Socket := aSocket;
  Accessed := False;
  FreeOnTerminate := true;
end;

constructor TThread_Connection_Keyboard.Create(aSocket: TCustomWinSocket);
begin
  inherited Create(False);
  Socket := aSocket;
  FreeOnTerminate := true;
end;

constructor TThread_Connection_Files.Create(aSocket: TCustomWinSocket);
begin
  inherited Create(False);
  Socket := aSocket;
  FreeOnTerminate := true;
end;
'''
'''
procedure Tfrm_Main.Clipboard_TimerTimer(Sender: TObject);
begin
  try
    try
      Clipboard.Open;

      if (Clipboard.HasFormat(CF_TEXT)) then
      begin
        if not(OldClipboardText = Clipboard.AsText) then
        begin
          OldClipboardText := Clipboard.AsText;
          Main_Socket.Socket.SendText('<|REDIRECT|><|CLIPBOARD|>' + Clipboard.AsText + '<|END|>');
        end;
      end;
    except
    end;
  finally
    Clipboard.Close;
  end;
end;
'''
'''
procedure Tfrm_Main.SetOffline;
begin
  YourID_Edit.Text := 'Offline';
  YourID_Edit.Enabled := False;

  YourPassword_Edit.Text := 'Offline';
  YourPassword_Edit.Enabled := False;

  TargetID_MaskEdit.Clear;
  TargetID_MaskEdit.Enabled := False;

  Connect_BitBtn.Enabled := False;

  Timeout_Timer.Enabled := False;
  Clipboard_Timer.Enabled := False;
end;

procedure SetConnected;
begin
  with frm_Main do
  begin
    YourID_Edit.Text := 'Receiving...';
    YourID_Edit.Enabled := False;

    YourPassword_Edit.Text := 'Receiving...';
    YourPassword_Edit.Enabled := False;

    TargetID_MaskEdit.Clear;
    TargetID_MaskEdit.Enabled := False;

    Connect_BitBtn.Enabled := False;
  end;
end;

procedure Tfrm_Main.SetOnline;
begin
  YourID_Edit.Text := MyID;
  YourID_Edit.Enabled := true;

  YourPassword_Edit.Text := MyPassword;
  YourPassword_Edit.Enabled := true;

  TargetID_MaskEdit.Clear;
  TargetID_MaskEdit.Enabled := true;

  Connect_BitBtn.Enabled := true;
end;

'''

'''
// Compress Stream with zLib
function CompressStreamWithZLib(SrcStream: TMemoryStream): Boolean;
var
  InputStream: TMemoryStream;
  inbuffer: Pointer;
  outbuffer: Pointer;
  count, outcount: longint;
begin
  Result := False;
  InputStream := TMemoryStream.Create;

  try
    InputStream.LoadFromStream(SrcStream);
    count := InputStream.Size;
    getmem(inbuffer, count);
    InputStream.ReadBuffer(inbuffer^, count);
    zcompress(inbuffer, count, outbuffer, outcount, zcDefault);
    SrcStream.Clear;
    SrcStream.Write(outbuffer^, outcount);
    Result := true;
  finally
    FreeAndNil(InputStream);
    FreeMem(inbuffer, count);
    FreeMem(outbuffer, outcount);
  end;
end;

// Decompress Stream with zLib
function DeCompressStreamWithZLib(SrcStream: TMemoryStream): Boolean;
var
  InputStream: TMemoryStream;
  inbuffer: Pointer;
  outbuffer: Pointer;
  count: longint;
  outcount: longint;
begin
  Result := False;
  InputStream := TMemoryStream.Create;

  try
    InputStream.LoadFromStream(SrcStream);
    count := InputStream.Size;
    getmem(inbuffer, count);
    InputStream.ReadBuffer(inbuffer^, count);
    zdecompress(inbuffer, count, outbuffer, outcount);
    SrcStream.Clear;
    SrcStream.Write(outbuffer^, outcount);
    Result := true;
  finally
    FreeAndNil(InputStream);
    FreeMem(inbuffer, count);
    FreeMem(outbuffer, outcount);
  end;
end;
'''
'''
botao de conectar
procedure Tfrm_Main.Connect_BitBtnClick(Sender: TObject);
begin
  if not(TargetID_MaskEdit.Text = '   -   -   ') then
  begin
    if (TargetID_MaskEdit.Text = MyID) then
      MessageBox(0, 'You can not connect with yourself!', 'AllaKore Remote', MB_ICONASTERISK + MB_TOPMOST)
    else
    begin
      Main_Socket.Socket.SendText('<|FINDID|>' + TargetID_MaskEdit.Text + '<|END|>');
      TargetID_MaskEdit.Enabled := False;
      Connect_BitBtn.Enabled := False;
      Status_Image.Picture.Assign(Image1.Picture);
      Status_Label.Caption := 'Finding the ID...';
    end;
  end;
end;
'''
'''
procedure Tfrm_Main.Desktop_SocketConnect(Sender: TObject; Socket: TCustomWinSocket);
begin
  // If connected, then send MyID for identification on Server
  Socket.SendText('<|DESKTOPSOCKET|>' + MyID + '<|END|>');
  Thread_Connection_Desktop := TThread_Connection_Desktop.Create(Socket);
end;
'''
'''
procedure Tfrm_Main.Files_SocketConnect(Sender: TObject; Socket: TCustomWinSocket);
begin
  Socket.SendText('<|FILESSOCKET|>' + MyID + '<|END|>');
  Thread_Connection_Files := TThread_Connection_Files.Create(Socket);
end;
'''
'''
procedure Tfrm_Main.FormCreate(Sender: TObject);
var
  _Host: AnsiString;
  _Port: Integer;
begin
  // Insert version on Caption of the Form
  Caption := Caption + ' - ' + GetAppVersionStr;

  // Reads two exe params - host and port. If not supplied uses constants. to use: client.exe HOST PORT, for ex. AllaKore_Remote_Client.exe 192.168.16.201 3398
  if (ParamStr(1) <> '') then
    _Host := ParamStr(1)
  else
    _Host := Host;

  if (ParamStr(2) <> '') then
    _Port := StrToIntDef(ParamStr(2), Port)
  else
    _Port := Port;

  // Define Host and Port
  Main_Socket := TClientSocket.Create(self);
  Main_Socket.Active := False;
  Main_Socket.ClientType := ctNonBlocking;
  Main_Socket.OnConnecting := Main_SocketConnecting;
  Main_Socket.OnConnect := Main_SocketConnect;
  Main_Socket.OnDisconnect := Main_SocketDisconnect;
  Main_Socket.OnError := Main_SocketError;
  Main_Socket.Host := _Host;
  Main_Socket.Port := _Port;

  Desktop_Socket := TClientSocket.Create(self);
  Desktop_Socket.Active := False;
  Desktop_Socket.ClientType := ctNonBlocking;
  Desktop_Socket.OnConnect := Desktop_SocketConnect;
  Desktop_Socket.OnError := Desktop_SocketError;
  Desktop_Socket.Host := _Host;
  Desktop_Socket.Port := _Port;

  Keyboard_Socket := TClientSocket.Create(self);
  Keyboard_Socket.Active := False;
  Keyboard_Socket.ClientType := ctNonBlocking;
  Keyboard_Socket.OnConnect := Keyboard_SocketConnect;
  Keyboard_Socket.OnError := Keyboard_SocketError;
  Keyboard_Socket.Host := _Host;
  Keyboard_Socket.Port := _Port;

  Files_Socket := TClientSocket.Create(self);
  Files_Socket.Active := False;
  Files_Socket.ClientType := ctNonBlocking;
  Files_Socket.OnConnect := Files_SocketConnect;
  Files_Socket.OnError := Files_SocketError;
  Files_Socket.Host := _Host;
  Files_Socket.Port := _Port;

  ResolutionTargetWidth := 986;
  ResolutionTargetHeight := 600;

  MyPing := 256;

  SetOffline;
  Reconnect;
end;
'''
''' <|KEYBOARDSOCKET|>
procedure Tfrm_Main.Keyboard_SocketConnect(Sender: TObject; Socket: TCustomWinSocket);
begin
  Socket.SendText('<|KEYBOARDSOCKET|>' + MyID + '<|END|>');
  Thread_Connection_Keyboard := TThread_Connection_Keyboard.Create(Socket);
end;
'''
'''
procedure Tfrm_Main.Main_SocketConnect(Sender: TObject; Socket: TCustomWinSocket);
begin
  Status_Image.Picture.Assign(Image3.Picture);
  Status_Label.Caption := 'You are connected!';
  Timeout := 0;
  Timeout_Timer.Enabled := true;
  Socket.SendText('<|MAINSOCKET|>');
  Thread_Connection_Main := TThread_Connection_Main.Create(Socket);
end;

procedure Tfrm_Main.Main_SocketConnecting(Sender: TObject; Socket: TCustomWinSocket);
begin
  Status_Image.Picture.Assign(Image1.Picture);
  Status_Label.Caption := 'Connecting to Server...';
end;

procedure Tfrm_Main.Main_SocketDisconnect(Sender: TObject; Socket: TCustomWinSocket);
begin
  if (frm_RemoteScreen.Visible) then
    frm_RemoteScreen.Close;

  SetOffline;

  Status_Image.Picture.Assign(Image2.Picture);
  Status_Label.Caption := 'Failed connect to Server.';

  CloseSockets;
end;

procedure Tfrm_Main.Main_SocketError(Sender: TObject; Socket: TCustomWinSocket; ErrorEvent: TErrorEvent; var ErrorCode: Integer);
begin
  ErrorCode := 0;

  if (frm_RemoteScreen.Visible) then
    frm_RemoteScreen.Close;

  SetOffline;

  Status_Image.Picture.Assign(Image2.Picture);
  Status_Label.Caption := 'Failed connect to Server.';

  CloseSockets;
end;
'''
'''
// Connection are Main
procedure TThread_Connection_Main.Execute;
var
  Buffer: string;
  BufferTemp: string;
  Extension: string;
  i: Integer;
  Position: Integer;
  MousePosX: Integer;
  MousePosY: Integer;
  FoldersAndFiles: TStringList;
  L: TListItem;
  FileToUpload: TFileStream;
  hDesktop: HDESK;
begin
  inherited;

  FoldersAndFiles := nil;
  FileToUpload := nil;

  while Socket.Connected do
  begin
    Sleep(ProcessingSlack); // Avoids using 100% CPU

    if (Socket = nil) or not(Socket.Connected) then
      Break;

    if Socket.ReceiveLength < 1 then
      Continue;

    Buffer := Socket.ReceiveText;

    // Received data, then resets the timeout
    Timeout := 0;

    // EUREKA: This is the responsable to interact with UAC. But we need run
    // the software on SYSTEM account to work.
    hDesktop := OpenInputDesktop(0, true, MAXIMUM_ALLOWED);
    if hDesktop <> 0 then
    begin
      SetThreadDesktop(hDesktop);
      CloseHandle(hDesktop);
    end;

    // If receive ID, are Online
    Position := Pos('<|ID|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 5);
      Position := Pos('<|>', BufferTemp);
      frm_Main.MyID := Copy(BufferTemp, 1, Position - 1);
      Delete(BufferTemp, 1, Position + 2);
      frm_Main.MyPassword := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);
      Synchronize(frm_Main.SetOnline);

      // If this Socket are connected, then connect the Desktop Socket, Keyboard Socket, File Download Socket and File Upload Socket
      Synchronize(
        procedure
        begin
          with frm_Main do
          begin
            Desktop_Socket.Active := true;
            Keyboard_Socket.Active := true;
            Files_Socket.Active := true;

            TargetID_MaskEdit.SetFocus;
          end;
        end);
    end;

    // Ping
    if Buffer.Contains('<|PING|>') then
      Socket.SendText('<|PONG|>');

    Position := Pos('<|SETPING|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 10);
      BufferTemp := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);
      frm_Main.MyPing := StrToInt(BufferTemp);
    end;

    // Warns access and remove Wallpaper
    if Buffer.Contains('<|ACCESSING|>') then
    begin
      OldWallpaper := GetWallpaperDirectory;
      // ChangeWallpaper('');

      Synchronize(
        procedure
        begin
          frm_Main.TargetID_MaskEdit.Enabled := False;
          frm_Main.Connect_BitBtn.Enabled := False;
          frm_Main.Status_Image.Picture.Assign(frm_Main.Image3.Picture);
          frm_Main.Status_Label.Caption := 'Connected support!';
        end);
      Accessed := true;
    end;

    if Buffer.Contains('<|IDEXISTS!REQUESTPASSWORD|>') then
    begin
      Synchronize(
        procedure
        begin
          frm_Main.Status_Label.Caption := 'Waiting for authentication...';
          frm_Password.ShowModal;
        end);
    end;

    if Buffer.Contains('<|IDNOTEXISTS|>') then
    begin
      Synchronize(
        procedure
        begin
          frm_Main.Status_Image.Picture.Assign(frm_Main.Image2.Picture);
          frm_Main.Status_Label.Caption := 'ID does nor exists.';
          frm_Main.TargetID_MaskEdit.Enabled := true;
          frm_Main.Connect_BitBtn.Enabled := true;
          frm_Main.TargetID_MaskEdit.SetFocus;
        end);
    end;

    if Buffer.Contains('<|ACCESSDENIED|>') then
    begin
      Synchronize(
        procedure
        begin
          frm_Main.Status_Image.Picture.Assign(frm_Main.Image2.Picture);
          frm_Main.Status_Label.Caption := 'Wrong password!';
          frm_Main.TargetID_MaskEdit.Enabled := true;
          frm_Main.Connect_BitBtn.Enabled := true;
          frm_Main.TargetID_MaskEdit.SetFocus;
        end);
    end;

    if Buffer.Contains('<|ACCESSBUSY|>') then
    begin
      Synchronize(
        procedure
        begin
          frm_Main.Status_Image.Picture.Assign(frm_Main.Image2.Picture);
          frm_Main.Status_Label.Caption := 'PC is Busy!';
          frm_Main.TargetID_MaskEdit.Enabled := true;
          frm_Main.Connect_BitBtn.Enabled := true;
          frm_Main.TargetID_MaskEdit.SetFocus;
        end);
    end;

    if Buffer.Contains('<|ACCESSGRANTED|>') then
    begin
      Synchronize(
        procedure
        begin
          frm_Main.Status_Image.Picture.Assign(frm_Main.Image3.Picture);
          frm_Main.Status_Label.Caption := 'Access granted!';
          frm_Main.Viewer := true;
          frm_Main.Clipboard_Timer.Enabled := true;
          frm_Main.ClearConnection;
          frm_RemoteScreen.Show;
          frm_Main.Hide;
          Socket.SendText('<|RELATION|>' + frm_Main.MyID + '<|>' + frm_Main.TargetID_MaskEdit.Text + '<|END|>');
        end);
    end;

    if Buffer.Contains('<|DISCONNECTED|>') then
    begin
      Synchronize(
        procedure
        begin
          frm_RemoteScreen.Hide;
          frm_ShareFiles.Hide;
          frm_Chat.Hide;

          // if Accessed then
          // ChangeWallpaper(OldWallpaper);

          frm_Main.ReconnectSecundarySockets;
          frm_Main.Show;
          frm_Main.SetOnline;
          frm_Main.Status_Image.Picture.Assign(frm_Main.Image2.Picture);
          frm_Main.Status_Label.Caption := 'Lost connection to PC!';
          FlashWindow(frm_Main.Handle, true);
        end);
    end;

    { Redirected commands }

    // Desktop Remote
    Position := Pos('<|RESOLUTION|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 13);
      Position := Pos('<|>', BufferTemp);
      frm_Main.ResolutionTargetWidth := StrToInt(Copy(BufferTemp, 1, Position - 1));
      Delete(BufferTemp, 1, Position + 2);
      frm_Main.ResolutionTargetHeight := StrToInt(Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1));
    end;

    Position := Pos('<|SETMOUSEPOS|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 14);
      Position := Pos('<|>', BufferTemp);
      MousePosX := StrToInt(Copy(BufferTemp, 1, Position - 1));
      Delete(BufferTemp, 1, Position + 2);
      MousePosY := StrToInt(Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1));
      SetCursorPos(MousePosX, MousePosY);
    end;

    Position := Pos('<|SETMOUSELEFTCLICKDOWN|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 24);
      Position := Pos('<|>', BufferTemp);
      MousePosX := StrToInt(Copy(BufferTemp, 1, Position - 1));
      Delete(BufferTemp, 1, Position + 2);
      MousePosY := StrToInt(Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1));
      SetCursorPos(MousePosX, MousePosY);
      Mouse_Event(MOUSEEVENTF_ABSOLUTE or MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
    end;

    Position := Pos('<|SETMOUSELEFTCLICKUP|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 22);
      Position := Pos('<|>', BufferTemp);
      MousePosX := StrToInt(Copy(BufferTemp, 1, Position - 1));
      Delete(BufferTemp, 1, Position + 2);
      MousePosY := StrToInt(Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1));
      SetCursorPos(MousePosX, MousePosY);
      Mouse_Event(MOUSEEVENTF_ABSOLUTE or MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
    end;

    Position := Pos('<|SETMOUSERIGHTCLICKDOWN|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 25);
      Position := Pos('<|>', BufferTemp);
      MousePosX := StrToInt(Copy(BufferTemp, 1, Position - 1));
      Delete(BufferTemp, 1, Position + 2);
      MousePosY := StrToInt(Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1));
      SetCursorPos(MousePosX, MousePosY);
      Mouse_Event(MOUSEEVENTF_ABSOLUTE or MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0);
    end;

    Position := Pos('<|SETMOUSERIGHTCLICKUP|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 23);
      Position := Pos('<|>', BufferTemp);
      MousePosX := StrToInt(Copy(BufferTemp, 1, Position - 1));
      Delete(BufferTemp, 1, Position + 2);
      MousePosY := StrToInt(Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1));
      SetCursorPos(MousePosX, MousePosY);
      Mouse_Event(MOUSEEVENTF_ABSOLUTE or MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0);
    end;

    Position := Pos('<|SETMOUSEMIDDLEDOWN|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 21);
      Position := Pos('<|>', BufferTemp);
      MousePosX := StrToInt(Copy(BufferTemp, 1, Position - 1));
      Delete(BufferTemp, 1, Position + 2);
      MousePosY := StrToInt(Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1));
      SetCursorPos(MousePosX, MousePosY);
      Mouse_Event(MOUSEEVENTF_ABSOLUTE or MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0);
    end;

    Position := Pos('<|SETMOUSEMIDDLEUP|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 19);
      Position := Pos('<|>', BufferTemp);
      MousePosX := StrToInt(Copy(BufferTemp, 1, Position - 1));
      Delete(BufferTemp, 1, Position + 2);
      MousePosY := StrToInt(Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1));
      SetCursorPos(MousePosX, MousePosY);
      Mouse_Event(MOUSEEVENTF_ABSOLUTE or MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0);
    end;

    Position := Pos('<|WHEELMOUSE|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 13);
      BufferTemp := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);
      Mouse_Event(MOUSEEVENTF_WHEEL, 0, 0, DWORD(StrToInt(BufferTemp)), 0);
    end;

    // Clipboard Remote
    Position := Pos('<|CLIPBOARD|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 12);
      BufferTemp := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);
      try
        Clipboard.Open;
        Clipboard.AsText := BufferTemp;
      finally
        Clipboard.Close;
      end;
    end;

    // Chat
    Position := Pos('<|CHAT|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 7);
      BufferTemp := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);

      Synchronize(
        procedure
        begin
          with frm_Chat do
          begin
            if (FirstMessage) then
            begin
              LastMessageAreYou := False;
              Chat_RichEdit.SelStart := Chat_RichEdit.GetTextLen;
              Chat_RichEdit.SelAttributes.Style := [fsBold];
              Chat_RichEdit.SelAttributes.Color := clGreen;
              Chat_RichEdit.SelText := #13 + #13 + 'He say:';
              FirstMessage := False;
            end;

            if (LastMessageAreYou) then
            begin
              LastMessageAreYou := False;
              Chat_RichEdit.SelStart := Chat_RichEdit.GetTextLen;
              Chat_RichEdit.SelAttributes.Style := [fsBold];
              Chat_RichEdit.SelAttributes.Color := clGreen;
              Chat_RichEdit.SelText := #13 + #13 + 'He say:' + #13;

              Chat_RichEdit.SelStart := Chat_RichEdit.GetTextLen;
              Chat_RichEdit.SelAttributes.Color := clWhite;
              Chat_RichEdit.SelText := '   •   ' + BufferTemp;
            end
            else
            begin
              Chat_RichEdit.SelStart := Chat_RichEdit.GetTextLen;
              Chat_RichEdit.SelAttributes.Style := [];
              Chat_RichEdit.SelAttributes.Color := clWhite;
              Chat_RichEdit.SelText := #13 + '   •   ' + BufferTemp;
            end;

            SendMessage(Chat_RichEdit.Handle, WM_VSCROLL, SB_BOTTOM, 0);

            if not(Visible) then
            begin
              PlaySound('BEEP', 0, SND_RESOURCE or SND_ASYNC);
              Show;
            end;

            if not(Active) then
            begin
              PlaySound('BEEP', 0, SND_RESOURCE or SND_ASYNC);
              FlashWindow(frm_Main.Handle, true);
              FlashWindow(frm_Chat.Handle, true);
            end;
          end;
        end);
    end;

    // Share Files
    // Request Folder List
    Position := Pos('<|GETFOLDERS|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 13);
      BufferTemp := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);
      Socket.SendText('<|REDIRECT|><|FOLDERLIST|>' + ListFolders(BufferTemp) + '<|ENDFOLDERLIST|>');
    end;

    // Request Files List
    Position := Pos('<|GETFILES|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 11);
      BufferTemp := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);
      Socket.SendText('<|REDIRECT|><|FILESLIST|>' + ListFiles(BufferTemp, '*.*') + '<|ENDFILESLIST|>');
    end;

    // Receive Folder List
    Position := Pos('<|FOLDERLIST|>', Buffer);
    if Position > 0 then
    begin
      while Socket.Connected do
      begin
        if Buffer.Contains('<|ENDFOLDERLIST|>') then
          Break;

        if Socket.ReceiveLength > 0 then
          Buffer := Buffer + Socket.ReceiveText;

        Sleep(ProcessingSlack);
      end;

      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 13);
      FoldersAndFiles := TStringList.Create;
      FoldersAndFiles.Text := Copy(BufferTemp, 1, Pos('<|ENDFOLDERLIST|>', BufferTemp) - 1);
      FoldersAndFiles.Sort;

      Synchronize(
        procedure
        var
          i: Integer;
        begin
          frm_ShareFiles.ShareFiles_ListView.Clear;

          for i := 0 to FoldersAndFiles.count - 1 do
          begin
            L := frm_ShareFiles.ShareFiles_ListView.Items.Add;
            if (FoldersAndFiles.Strings[i] = '..') then
            begin
              L.Caption := 'Return';
              L.ImageIndex := 0;
            end
            else
            begin
              L.Caption := FoldersAndFiles.Strings[i];
              L.ImageIndex := 1;
            end;
            frm_ShareFiles.Caption := 'Share Files - ' + IntToStr(frm_ShareFiles.ShareFiles_ListView.Items.count) + ' Items found';
          end;
        end);

      FreeAndNil(FoldersAndFiles);
      Socket.SendText('<|REDIRECT|><|GETFILES|>' + frm_ShareFiles.Directory_Edit.Text + '<|END|>');
    end;

    // Receive Files List
    Position := Pos('<|FILESLIST|>', Buffer);
    if Position > 0 then
    begin
      while Socket.Connected do
      begin
        if Buffer.Contains('<|ENDFILESLIST|>') then
          Break;

        if Socket.ReceiveLength > 0 then
          Buffer := Buffer + Socket.ReceiveText;

        Sleep(ProcessingSlack);
      end;

      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 12);
      FoldersAndFiles := TStringList.Create;
      FoldersAndFiles.Text := Copy(BufferTemp, 1, Pos('<|ENDFILESLIST|>', BufferTemp) - 1);
      FoldersAndFiles.Sort;

      Synchronize(
        procedure
        var
          i: Integer;
        begin
          for i := 0 to FoldersAndFiles.count - 1 do
          begin
            L := frm_ShareFiles.ShareFiles_ListView.Items.Add;
            L.Caption := FoldersAndFiles.Strings[i];
            Extension := LowerCase(ExtractFileExt(L.Caption));

            if (Extension = '.exe') then
              L.ImageIndex := 3
            else if (Extension = '.txt') then
              L.ImageIndex := 4
            else if (Extension = '.rar') then
              L.ImageIndex := 5
            else if (Extension = '.mp3') then
              L.ImageIndex := 6
            else if (Extension = '.zip') then
              L.ImageIndex := 7
            else if (Extension = '.jpg') then
              L.ImageIndex := 8
            else if (Extension = '.bat') then
              L.ImageIndex := 9
            else if (Extension = '.xml') then
              L.ImageIndex := 10
            else if (Extension = '.sql') then
              L.ImageIndex := 11
            else if (Extension = '.html') then
              L.ImageIndex := 12
            else if (Extension = '.xls') then
              L.ImageIndex := 13
            else if (Extension = '.png') then
              L.ImageIndex := 14
            else if (Extension = '.doc') then
              L.ImageIndex := 15
            else if (Extension = '.docx') then
              L.ImageIndex := 15
            else if (Extension = '.pdf') then
              L.ImageIndex := 16
            else if (Extension = '.dll') then
              L.ImageIndex := 17
            else
              L.ImageIndex := 2;

            frm_ShareFiles.Caption := 'Share Files - ' + IntToStr(frm_ShareFiles.ShareFiles_ListView.Items.count) + ' Items found';
          end;

          frm_ShareFiles.Directory_Edit.Enabled := true;
          frm_ShareFiles.Caption := 'Share Files - ' + IntToStr(frm_ShareFiles.ShareFiles_ListView.Items.count) + ' Items found';
        end);

      FreeAndNil(FoldersAndFiles);
    end;

    Position := Pos('<|UPLOADPROGRESS|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 17);
      BufferTemp := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);

      Synchronize(
        procedure
        begin
          frm_ShareFiles.Upload_ProgressBar.Position := StrToInt(BufferTemp);
          frm_ShareFiles.SizeUpload_Label.Caption := 'Size: ' + GetSize(frm_ShareFiles.Upload_ProgressBar.Position) + ' / ' + GetSize(frm_ShareFiles.Upload_ProgressBar.Max);
        end);
    end;

    if Buffer.Contains('<|UPLOADCOMPLETE|>') then
    begin
      Synchronize(
        procedure
        begin
          frm_ShareFiles.Upload_ProgressBar.Position := 0;
          frm_ShareFiles.Upload_BitBtn.Enabled := true;
          frm_ShareFiles.Directory_Edit.Enabled := False;
          frm_ShareFiles.SizeUpload_Label.Caption := 'Size: 0 B / 0 B';
        end);

      frm_Main.Main_Socket.Socket.SendText('<|REDIRECT|><|GETFOLDERS|>' + frm_ShareFiles.Directory_Edit.Text + '<|END|>');

      Synchronize(
        procedure
        begin
          MessageBox(0, 'The file was successfully sent.', 'AllaKore Remote - Share Files', MB_ICONASTERISK + MB_TOPMOST);
        end);
    end;

    Position := Pos('<|DOWNLOADFILE|>', Buffer);
    if Position > 0 then
    begin
      BufferTemp := Buffer;
      Delete(BufferTemp, 1, Position + 15);
      BufferTemp := Copy(BufferTemp, 1, Pos('<|END|>', BufferTemp) - 1);
      FileToUpload := TFileStream.Create(BufferTemp, fmOpenRead);
      frm_Main.Files_Socket.Socket.SendText('<|SIZE|>' + IntToStr(FileToUpload.Size) + '<|END|>');
      frm_Main.Files_Socket.Socket.SendStream(FileToUpload);
    end;
  end;
end;
'''