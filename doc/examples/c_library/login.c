/*
Simple system that validates passwords and user names. There are two users in
system with valid user name and password. "demo mode" and "john long". All 
other user names are invalid. 
*/

#include <string.h>
#define NR_USERS 2

struct User {
    const char* name;
    const char* password;
};
const struct User VALID_USERS[NR_USERS] = { "john", "long", "demo", "mode" };

int validate_user(const char* name, const char* password) {
    int i;
    for (i = 0; i < NR_USERS; i++) {
        if (0 == strncmp(VALID_USERS[i].name, name, strlen(VALID_USERS[i].name)))
            if (0 == strncmp(VALID_USERS[i].password, password, strlen(VALID_USERS[i].password)))
                return 1;
    }    
    return 0;
}
