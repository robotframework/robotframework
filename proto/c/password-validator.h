/* 
Simple system that validates passwords and user names. There are two users in
system with valid user name and password. "demo mode" and "long john". All 
other user names are invalid. 
*/

/* Valid user return 1 */
int validate_user(const char* name, const char* password);
