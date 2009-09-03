/*
#  Copyright 2009 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
*/

#include <stdio.h>
#include <string.h>
#include "password-validator.h"

struct User
{
    const char* name;
    const char* password;
};

#define NR_USERS 2

const struct User VALID_USERS[NR_USERS] = { "john" , "long", "demo", "mode" };

const int MAX_LEN = 100;

/*
Simple system that validates passwords and user names. There are two users in
system with valid user name and password. "demo mode" and "john long". All 
other user names are invalid. 

System has command line interface and direct api for testing.
*/


/*
This is api that is called from python class to validate user.
*/
int validate_user(const char* name, const char* password) {

    int i;
    for (i = 0; i < NR_USERS; ++i)
    {
        if (0 == strncmp(VALID_USERS[i].name, name, strlen(VALID_USERS[i].name)))
            if (0 == strncmp(VALID_USERS[i].password, password, strlen(VALID_USERS[i].password)))
                return 1;
    }
    
    return 0;
}

int main(int argc, char* argv) { 
    char password[MAX_LEN];
    char username[MAX_LEN];
    printf("Give username: ");
    scanf("%s", username);

    printf("Give password: ");
    scanf("%s", password);

    if (validate_user(username, password))
        printf("Hello %s you are now in system\n", username);
    else
        printf("Incorrect username and password combination\n");
}
