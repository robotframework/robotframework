#include <stdio.h>
#include "passwordvalidatorstub.h"
#include "password-validator.h"

int check_password(const char* name, const char* user) {
	printf("check_password: %s/%s\n", name, user);
	return validate_user(name, user);
}


