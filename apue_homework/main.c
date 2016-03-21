/*
apue homework-by lifan
a simple shell interpreter
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>

#define MAX_CMD_LENGTH 255
#define MAX_NUM_OF_PARAMS 10
const char *MY_ENV = "MY_ENV";
static char *my_env_value = "->";

typedef enum {
    IN,
    OUT,
    ERR_OUT
}STD_FILE_DESC;

char *get_my_env();
int do_command(char *);
void file_redirect(char **cmd, char *filename, int in_or_out);


char* get_my_env(){
    char *env_str;
    if((env_str = getenv(MY_ENV)) != NULL){
        my_env_value = env_str;
    }
    return my_env_value;
}

char* join_params(char** params, int count){
    int  i=0;
    char *cmd=params[i++];
    while (i<count){
        strcat(cmd, " ");
        strcat(cmd, params[i]);
        i++;
    }
    return cmd;
}

char* get_current_dir(void){
    char buf[PATH_MAX+1];
    char *cwd = getcwd(buf, PATH_MAX+1);
    return cwd;
}

void add_cur_dir_to_path(void){
    char *path = getenv("PATH");
    strcat(path, ":");
    strcat(path, get_current_dir());
    setenv("PATH", path, 1);
}

void file_redirect(char **cmd, char *filename, int in_or_out){
    int fd;

    int pid;
    fflush(0);
    if ((pid=fork()) < 0){
        printf("fork error");
    } else if (pid == 0){ /* child */
        if (in_or_out==IN){
            //输入重定向
            fd = open(filename, O_RDONLY, 0);
            dup2(fd, STDIN_FILENO);
            close(fd);
        } else if (in_or_out==OUT){
            //输出重定向
            fd = open(filename, O_CREAT | O_WRONLY | O_TRUNC, 0644);
            dup2(fd, STDOUT_FILENO);
            close(fd);
        }else{

        }
        if (execvp(cmd[0], cmd) < 0){
            fprintf(stderr, "execvp error\n");
            kill(getpid(), SIGTERM);
            return;
        }

    } else{ /* father */
        waitpid(pid, NULL, 0);
    }
}

int do_command(char *command){
    int status;

    //split command
    int args_num = 0;
    char **params = (char **)malloc(MAX_CMD_LENGTH);
    params[args_num++] = strtok(command, " ");
    while ((params[args_num] = strtok(NULL, " ")) != NULL)
        args_num++;

    //input and output redirect
    int i=0;
    char *filename;
    char **cmd = (char **)malloc(MAX_CMD_LENGTH);
    int in_or_out = 0; //0-in, i-out
    while (i<args_num && params[i]){
        if (!strcmp(params[i], ">>") || !strcmp(params[i], "<<")){
            if (i+1 != args_num-1) {
                perror("output redirect must be one file");
                return -1;
            }
            filename = params[i+1];
            in_or_out = !strcmp(params[i], ">>") ? 1 : 0;
            file_redirect(cmd, filename, in_or_out);
            return 0;
        } else{
            cmd[i] = params[i];
        }
        i++;
    }

    if (!strcmp(params[0], "setenv")){
        if (args_num != 3) {
            perror("command \"export\" arguments error");
            return -1;
        }
        if (setenv(params[1], params[2], 1)){
            printf("could not set env value for %s\n", params[1]);
            return -1;
        }
    }
    else if (!strcmp(params[0], "quit") || !strcmp(params[0], "exit") || !strcmp(params[0], "close")){
        if (args_num != 1) {
            printf("command \"%s\" has no arguments", params[0]);
            return -1;
        }
        exit(0);
    }
    else if (!strcmp(params[0], "bg")){
        char **new_params = params + 1;
        args_num -= 1;

        int pid;
        if ((pid=fork()) < 0){
            printf("fork error");
        } else if (pid == 0) {
            //child
            if (execvp(new_params[0], new_params) < 0){
                printf("execvp error");
                kill(getpid(), SIGTERM);
                exit(-1);
            }
            exit(0);
        }else{
            printf("background process id is %d\n", pid);
            return 0;
        }
    }
    else{
        if (system(command) < 0)
            perror("call system function error\n");
    }
    return 0;
}


int main(void){
    char buf[MAX_CMD_LENGTH];

    add_cur_dir_to_path();

    printf("%s", get_my_env());
    while (fgets(buf, MAX_CMD_LENGTH, stdin) != NULL){
        if (buf[strlen(buf)-1] == '\n')
            buf[strlen(buf)-1] = '\0';

        //if cmd is empty, continue next command
        if (strtok(strdup(buf), "\n\t") == NULL){
            printf("%s", get_my_env());
            continue;
        }

        do_command(buf);
        printf("%s", get_my_env());
    }
}
