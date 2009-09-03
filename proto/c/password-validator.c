/*
Copyright Ran Nyman 2009
Licenced under apache 2.0 license.
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

/*const char* JOHN = "john";
const char* LONG = "long";

const char* DEMO = "demo";
const char* MODE = "mode";
*/
const int MAX_LEN = 100;

/*
Simple system that validates passwords and user names. There are two users in
system with valid user name and password. "demo mode" and "long john". All 
other user names are invalid. 

System has command line interface and direct api for testing.
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

int check_password(const char* name, const char* user) {
	return validate_user(name, user);
}

int main(int argc, char* argv) {
	char password[MAX_LEN];
	char username[MAX_LEN];
	printf("Give username: ");
	scanf("%s", username);

	printf("Give password: ");
	scanf("%s", password);

	if (validate_user(username, password))
		printf("Hello %s you now are in system\n", username);
	else
		printf("Incorrect username and password combination\n");
}
