#!/bin/bash
ftp -n<<!
open 127.0.0.1
user Anonymou Anonymous
binary
pwd
close
bye
!