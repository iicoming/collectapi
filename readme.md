
### 从java代码里提取api、请求方法、参数等信息，进行api资产管理

```

127.0.0.1:6379> lrange apis 1 10
1) "{\"api\": \"/book/{bookId}/detail\", \"timestamp\": \"2020-08-01\", \"git_address\": \"https://github.com/xxx/ssm.git\", \"branch\": \"master_f3f90d7\", \"method\": \"request\", \"parameters\": \"Long__bookId||Model__model\"}"
2) "{\"api\": \"/book/list\", \"timestamp\": \"2020-08-01\", \"git_address\": \"https://github.com/xxx/ssm.git\", \"branch\": \"master_f3f90d7\", \"method\": \"request\", \"parameters\": \"Model__model\"}"

```