/* 
Code will allow removal even if there are foriegn key references 
*/
SET FOREIGN_KEY_CHECKS=0;
DELETE FROM twitter_users WHERE id = 1001970347564990464;
SET FOREIGN_KEY_CHECKS=1
