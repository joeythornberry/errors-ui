LControl & n::
{

    SendInput "{LControl down}l{LControl up}"
    SendInput "python3 homework.py test.db {Enter}"
    Sleep 500

    ; choose class
    SendInput "scL"
    Sleep 500

    ; create new type
    SendInput "a bot made this"
    SendInput "{Enter}RL"
    Sleep 500

    ; fill out number of correct problems
    SendInput "5HHJ"
    Sleep 500

    ; fill out type of one error
    SendInput "a bL"

    ; fill out points lost of that error
    SendInput "3J"
    Sleep 500

    ; fill out points of another error
    SendInput "10H"
    ; fail to fill out its type
    SendInput "uJ"
    Sleep 500

    ; fill out type of a third error, but not its points
    SendInput "a bL"

    ; test all four directions for out of bounds
    SendInput "JJJJJJJJ"
    SendInput "KKKKKKKK"
    SendInput "LLLLLLLL"
    SendInput "HHHHHHHH"

    Sleep 500

    ; close out
    SendInput "Q"
    Sleep 500
    SendInput "y{Enter}"
}
