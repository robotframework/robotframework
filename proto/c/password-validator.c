/*
Copyright Ran Nyman 2009
Licenced under apache 2.0 license.
*/

#include <stdio.h>
#include <string.h>
#include "password-validator.h"


const char* JOHN = "john";
const char* LONG = "long";

const char* DEMO = "demo";
const char* MODE = "mode";

const int MAX_LEN = 100;

/*
Simple system that validates passwords and user names. There are two users in
system with valid user name and password. "demo mode" and "long john". All 
other user names are invalid. 

System has command line interface and direct api for testing.
*/

int validate_user(const char* name, const char* password) {
	if (0 == strncmp(LONG, name, strlen(LONG)))
		if (0 == strncmp(JOHN, password, strlen(JOHN)))
			return 1;

	if (0 == strncmp(DEMO, name, strlen(DEMO)))
		if (0 == strncmp(MODE, password, strlen(MODE)))
			return 1;
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
		printf("Hello %s you now are in system\n", username);
	else
		printf("Incorrect username and password combination\n");
}
