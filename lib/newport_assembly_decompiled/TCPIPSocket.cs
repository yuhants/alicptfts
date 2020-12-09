// Decompiled with JetBrains decompiler
// Type: Newport.Communication.TCPIP.TCPIPSocket
// Assembly: Newport.XPS.CommandInterface, Version=2.2.1.0, Culture=neutral, PublicKeyToken=9a267756cf640dcf
// MVID: FB71B87E-FF83-46E0-92C4-9A4818ED93EA
// Assembly location: C:\Windows\Microsoft.NET\assembly\GAC_64\Newport.XPS.CommandInterface\v4.0_2.2.1.0__9a267756cf640dcf\Newport.XPS.CommandInterface.dll

using System;
using System.Net.Sockets;
using System.Text;

namespace Newport.Communication.TCPIP
{
  public class TCPIPSocket
  {
    private const int NO_ERROR = 0;
    private const int PORT = 5001;
    private const string HOST = "192.168.33.3";
    private const string END_FLAG = "EndOfAPI";
    private const int SENDING_TIMEOUT = 1000;
    private const int READING_TIMEOUT = 1000;
    private const int RECEIVED_BUFFER_SIZE = 256;
    private string m_TCPAddress;
    private int m_TCPPort;
    private Socket m_socket;
    private string m_lastErrorMessage;

    public TCPIPSocket()
    {
      this.m_socket = (Socket) null;
      this.m_TCPPort = 5001;
      this.m_TCPAddress = string.Empty;
      this.m_lastErrorMessage = string.Empty;
    }

    public string GetLastError() => this.m_lastErrorMessage;

    public bool IsConnected() => this.m_socket != null && this.m_socket.Connected;

    public int DeviceOpen(string add, int port, int timeout)
    {
      this.m_lastErrorMessage = string.Empty;
      try
      {
        this.m_TCPAddress = add;
        this.m_TCPPort = port;
        this.m_socket = this.OpenSocket(this.m_TCPAddress, this.m_TCPPort);
        return this.m_socket == null ? -2 : this.SetTimeout(this.m_socket, 1000, timeout);
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    public int DeviceTimeout(int sendingTimeout, int readingTimeout)
    {
      this.m_lastErrorMessage = string.Empty;
      try
      {
        return this.SetTimeout(this.m_socket, sendingTimeout, readingTimeout);
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    public int DeviceClose()
    {
      this.m_lastErrorMessage = string.Empty;
      try
      {
        this.CloseSocket(this.m_socket);
        return 0;
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    public int DeviceWrite(string command)
    {
      this.m_lastErrorMessage = string.Empty;
      try
      {
        return this.Send(this.m_socket, command);
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    public int DeviceRead(out string response)
    {
      this.m_lastErrorMessage = string.Empty;
      response = string.Empty;
      try
      {
        return this.Receive(this.m_socket, out response);
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    public int DeviceQuery(string command, out string response)
    {
      this.m_lastErrorMessage = string.Empty;
      response = string.Empty;
      try
      {
        return this.SendReceive(this.m_socket, command, out response);
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    private Socket OpenSocket(string host, int port)
    {
      this.m_lastErrorMessage = string.Empty;
      try
      {
        Socket socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        socket?.Connect(host, port);
        return socket;
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return (Socket) null;
      }
    }

    private int SetTimeout(Socket s, int SendTimeoutMilliseconds, int ReceiveTimeoutMilliseconds)
    {
      this.m_lastErrorMessage = string.Empty;
      try
      {
        int num = 0;
        if (s != null)
        {
          s.SendTimeout = SendTimeoutMilliseconds;
          s.ReceiveTimeout = ReceiveTimeoutMilliseconds;
        }
        else
          num = -2;
        return num;
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    private void CloseSocket(Socket s)
    {
      this.m_lastErrorMessage = string.Empty;
      try
      {
        s?.Close();
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
      }
    }

    private int Send(Socket s, string request)
    {
      this.m_lastErrorMessage = string.Empty;
      try
      {
        int num = 0;
        byte[] bytes = Encoding.ASCII.GetBytes(request);
        if (s != null)
        {
          if (s.Send(bytes, bytes.Length, SocketFlags.None) < bytes.Length)
            num = -1;
        }
        else
          num = -2;
        return num;
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    private int Receive(Socket s, out string response)
    {
      this.m_lastErrorMessage = string.Empty;
      response = string.Empty;
      try
      {
        int num = 0;
        byte[] numArray = new byte[256];
        string empty = string.Empty;
        if (s != null)
        {
          int count;
          do
          {
            count = s.Receive(numArray, numArray.Length, SocketFlags.None);
            if (count > 0)
              empty += Encoding.ASCII.GetString(numArray, 0, count);
          }
          while (count > 0 && empty.IndexOf("EndOfAPI") == -1);
          response = empty;
        }
        else
          num = -2;
        return num;
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }

    private int SendReceive(Socket s, string request, out string response)
    {
      this.m_lastErrorMessage = string.Empty;
      response = string.Empty;
      try
      {
        int num;
        if (s != null)
        {
          num = this.Send(s, request);
          if (num == 0)
          {
            string response1 = string.Empty;
            num = this.Receive(s, out response1);
            if (num == 0)
              response = response1;
          }
        }
        else
          num = -2;
        return num;
      }
      catch (Exception ex)
      {
        this.m_lastErrorMessage = ex.Message;
        return -1;
      }
    }
  }
}
