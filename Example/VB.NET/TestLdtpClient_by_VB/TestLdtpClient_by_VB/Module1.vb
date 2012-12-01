Module Module1

    Sub Main()
        Dim ldtp As New Ldtp.Ldtp("*Notepad")
        Console.WriteLine("Notepad: " + ldtp.GuiExist().ToString())
        Console.WriteLine("Word Wrap: " + ldtp.VerifyMenuCheck("mnuFormat;mnuWordWrap").ToString())
    End Sub

End Module