# 运行报告

## 运行环境

- 运行日期：2026-08-05（Asia/Tokyo）
- Python 版本：3.14.6
- Playwright 版本：1.62.0
- Python 解释器：`D:\kaifa\Dome\.venv314\Scripts\python.exe`
- 浏览器环境：由 Playwright 管理的 Chromium，无头模式

## 第一次完整运行

运行命令：

```powershell
D:\kaifa\Dome\.venv314\Scripts\python.exe -m src.main --pages 10 --output outputs/movies_final.jsonl
```

统计结果：

| 指标 |            结果 |
| --- |--------------:|
| page_completed |            10 |
| url_discovered |           100 |
| success |           100 |
| failed |             0 |
| skipped |             0 |
| retries |             0 |
| elapsed_seconds | 141.10451450000983 |
| 输出文件唯一 URL 数 |           100 |

第一次运行生成了现有的 `outputs/movies_final.jsonl`。创建本报告时，已对该文件内容进行独立校验。

## 第二次完整运行

运行命令：

```powershell
D:\kaifa\Dome\.venv314\Scripts\python.exe -m src.main --pages 10 --output outputs/movies_final.jsonl
```

2026-08-05 实际记录的统计结果：

| 指标 | 结果 |
| --- | ---: |
| page_completed | 10 |
| url_discovered | 100 |
| success | 0 |
| failed | 0 |
| skipped | 100 |
| retries | 0 |
| elapsed_seconds | 16.622431499999948 |
| 输出文件唯一 URL 数 | 100 |

## 输出文件检查

文件：`outputs/movies_final.jsonl`

| 检查项 | 结果 |
| --- | ---: |
| JSONL 行数 | 100 |
| 合法 JSON 记录数 | 100 |
| 非法 JSON 记录数 | 0 |
| 唯一 URL 数量 | 100 |
| 字段不符合要求的记录数 | 0 |
| 包含敏感字段的记录数 | 0 |

每条记录都恰好包含以下六个字段：

- `url`
- `name`
- `cover`
- `drama`
- `categories`
- `score`

UTF-8 中文内容能够正常解码，没有发现乱码。数据中未发现 Cookie、Authorization 或完整请求头等敏感信息。

## 测试结果

运行命令：

```powershell
D:\kaifa\Dome\.venv314\Scripts\python.exe -m pytest -q
```

测试结果：

```text
31 passed in 0.17s
```

测试使用假的 Playwright 对象和临时目录，不会启动真实浏览器，也不会访问外部网站。

## 验收结论

爬虫成功完成 10 个列表页，发现 100 个唯一详情 URL。最终 JSONL 文件包含 100 条合法且 URL 唯一的电影记录。

使用完全相同的命令再次运行时，程序不会重复采集已经存储的详情页，也不会追加重复数据：第二次新增 0 条、跳过 100 条，输出文件仍然保持为 100 行。

两次完整运行均未发生采集失败或重试，第二次运行正确跳过了全部 100 个已存储 URL。
