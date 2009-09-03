CC=gcc
CFLAGS=-I.
OBJ = password-validator.o

libpasswordvalidatorstub: $(OBJ)
	$(CC) -shared -Wl,-soname,libpasswordvalidatorstub.so.1 -o libpasswordvalidatorstub.so.1.0.0 password-validator.o

password-validator: $(OBJ) password-validator.h
	$(CC) -o $@ $^ $(CFLAGS)

libpasswordvalidatorstub: password-validator

clean:
	rm -f $(OBJ) 
	rm -f libpasswordvalidatorstub.so.1.0.0
	rm -f password-validator
	rm -f PasswordValidator.pyc
