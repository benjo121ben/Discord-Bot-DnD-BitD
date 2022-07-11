from src.GlobalVariables import charDic


# This checks in case of missing parameters or invalid amounts. does not cover multiple versions of same Command
def check_command_arg_len(supposed_len, *args):
    if len(args) != supposed_len:
        print("command has invalid argunments")
        return False
    return True


# is there to avoid functions being called on a character that doesn't exist
def check_char_name(char_name):
    print(char_name)
    if char_name in charDic.keys():
        return True
    else:
        print("Character doesn't exist")
        return False