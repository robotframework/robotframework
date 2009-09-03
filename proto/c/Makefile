CC=gcc
CFLAGS=-I.
SO_CFLAGS=-fPIC. 
DEPS = password-validator.h passwordvalidatorstub.h
OBJ = password-validator.o
OBJ_STUB = passwordvalidatorstub.o

libpasswordvalidatorstub: $(OBJ_STUB)
	$(CC) -shared -Wl,-soname,libpasswordvalidatorstub.so.1 -o libpasswordvalidatorstub.so.1.0.0 password-validator.o

#passwordvalidatorstub: $(OBJ) $(OBJ_STUB) password-validator
#	$(CC) -o $@ $^ $(SO_CFLAGS)

password-validator: $(OBJ) password-validator.h
	$(CC) -o $@ $^ $(CFLAGS)

libpasswordvalidatorstub: password-validator

clean:
	rm -f $(OBJ) 
	rm -f $(OBJ_STUB)
	rm -f libpasswordvalidatorstub.so.1.0.0
	rm -f passwordvalidatorstub
	rm -f password-validator
	rm -f PasswordValidator.pyc
