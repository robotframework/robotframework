#include "passwordvalidatorstub.h"
#include "password-validator.h"

int check_password(const char* name, const char* user) {
	return validate_user(name, user);
}


