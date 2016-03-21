##C语言实现简单的shell解释器

###使用说明

使用C语言实现一个简单的shell解释器，包含以下功能:

* 程序启动显示命令提示符->，修改提示符: setenv MY_ENV %会将提示符修改为%
* 程序内输入命令exit或quit或close或按下CTRL+C键可退出
* 命令bg command 可将command放在后台执行
* 使用">>"重定向输出，"<<"重定向输入


###代码说明

进入源码目录直接编译: gcc main.c -o simple_shell

* main函数内无限循环，重复读取程序输入
* int do_command(char *);处理每条输入的命令
* char *get_my_env();获取自定义环境变量MY_ENV的值，如果不存在返回“->”
* void file_redirect(char **cmd, char *filename, int in_or_out);完成输入输出重定向

###测试

* ls
* setenv MY_ENV %
* setenv MY_ENV ->
* bg ./sleep.sh
* ls >> tmp
* cat << tmp
* close

>注:以上几条在mac os上运行无误



