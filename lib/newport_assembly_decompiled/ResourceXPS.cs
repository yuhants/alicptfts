// Decompiled with JetBrains decompiler
// Type: Newport.XPS.ResourceXPS
// Assembly: Newport.XPS.CommandInterface, Version=2.2.1.0, Culture=neutral, PublicKeyToken=9a267756cf640dcf
// MVID: FB71B87E-FF83-46E0-92C4-9A4818ED93EA
// Assembly location: C:\Windows\Microsoft.NET\assembly\GAC_64\Newport.XPS.CommandInterface\v4.0_2.2.1.0__9a267756cf640dcf\Newport.XPS.CommandInterface.dll

using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.Resources;
using System.Runtime.CompilerServices;

namespace Newport.XPS
{
  [GeneratedCode("System.Resources.Tools.StronglyTypedResourceBuilder", "4.0.0.0")]
  [DebuggerNonUserCode]
  [CompilerGenerated]
  internal class ResourceXPS
  {
    private static ResourceManager resourceMan;
    private static CultureInfo resourceCulture;

    internal ResourceXPS()
    {
    }

    [EditorBrowsable(EditorBrowsableState.Advanced)]
    internal static ResourceManager ResourceManager
    {
      get
      {
        if (ResourceXPS.resourceMan == null)
          ResourceXPS.resourceMan = new ResourceManager("Newport.XPS.ResourceXPS", typeof (ResourceXPS).Assembly);
        return ResourceXPS.resourceMan;
      }
    }

    [EditorBrowsable(EditorBrowsableState.Advanced)]
    internal static CultureInfo Culture
    {
      get => ResourceXPS.resourceCulture;
      set => ResourceXPS.resourceCulture = value;
    }

    internal static string Error_001 => ResourceXPS.ResourceManager.GetString(nameof (Error_001), ResourceXPS.resourceCulture);

    internal static string Error_005 => ResourceXPS.ResourceManager.GetString(nameof (Error_005), ResourceXPS.resourceCulture);

    internal static string Error_007 => ResourceXPS.ResourceManager.GetString(nameof (Error_007), ResourceXPS.resourceCulture);
  }
}
