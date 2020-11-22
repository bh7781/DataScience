import re


def is_valid_name(name_str):
    """
    Method to validate name field.
    Input : name (allowed datatypes : string)
    Output : Boolean (True if valid else False)
    """
    # Check whether the input string is empty or not
    if name_str == '':
        print('Blank values are not allowed.')
        return bool(0)
    # Check whether the input string contains whitespace or not
    if bool(re.search(r"\s", name_str)):
        print('Space not allowed in this field.')
        return bool(0)
    
    # Check whether the input string contains only alphabets or dot(s) or not
    pattern = r'^(?!^\.)(?!.*[\.]$)[A-Za-z\.]*$'
    is_valid = bool(re.match(pattern, name_str))
    print(is_valid)
    if is_valid == bool(False):
        print('Only alphabets and dot(s) are allowed in name string.')

    else:
        print('INVALID FORMAT')
        return bool(0)


def is_valid_mobNo(mob_no):
    """
    Method to validate mobile number.
    Input : mobile_number (allowed datatypes : int, string)
    Output : Boolean (True if valid else False)
    """
    mob_no = str(mob_no)
    # Regular expression to check whether the input contains only integers of exact length 10.
    return bool(re.match("^[0-9]{10}$", mob_no))


def is_valid_password1(pw_string):
    """
    Method to validate password.
    Input : password (allowed datatype : any)
    Output : Boolean (True if valid else False)
    """
    # Regular expression to check whether the input password meets required criteria or not
    # Criteria1: Password should contain atleast 1 lowercase letter
    # Criteria2: Password should contain atleast 1 uppercase letter
    # Criteria3: Password should contain atleast 1 numeric character
    # Criteria4: Password should contain atleast 1 Special Symbol (@,$,!,%,*,#,?,&)
    # Criteria3: Password length should be min 8 to max 16 charaters.

    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,16}$"
    pat = re.compile(reg)
    mat = re.search(pat, pw_string)
    if mat:
        print("Password is valid.")
        return bool(1)
    else:
        print("Password invalid !!")
        return bool(0)

def capitalize_name(input_name):
    """
    Method to capitalize first character of name.
    If '.' is present in string then first character of every list 
    element after splitting input string by '.'  is capitalized.
    This method should be called iff is_valid_name() returns True.
    Input : name (allowed)
    Output : Capitalized name
    """
    splitted_name = input_name.split('.')
    word_list = []
    for word in splitted_name:
        word_list.append(word[0].upper() + word[1:])
    return ('.'.join(word_list))
