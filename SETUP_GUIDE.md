# 🎾 Tennis Life - Google Sheets 配置指南

## 📋 配置步骤

### 1️⃣ 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目（如 `tennis-life`）
3. 启用以下 API：
   - Google Sheets API
   - Google Drive API

### 2️⃣ 创建服务账号

1. 在 Google Cloud Console → IAM 和管理 → 服务账号
2. 点击「创建服务账号」
3. 填写名称（如 `tennis-life-bot`）
4. 点击「创建并继续」→ 完成
5. 点击创建的服务账号 → 密钥 → 添加密钥 → 创建新密钥 → JSON
6. 下载 JSON 文件（保存好！）

### 3️⃣ 创建 Google Sheet

1. 访问 [Google Sheets](https://sheets.google.com/)
2. 创建新的空白表格
3. 重命名为 `Tennis Life Data`
4. 复制表格 URL（类似 `https://docs.google.com/spreadsheets/d/XXXXX/edit`）
5. 点击「共享」→ 添加服务账号邮箱（在 JSON 文件中的 `client_email`）
6. 权限选择「编辑者」

### 4️⃣ 配置 Streamlit Secrets

#### 本地开发
在项目目录创建 `.streamlit/secrets.toml`：

```toml
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service%40your-project.iam.gserviceaccount.com"
```

⚠️ **注意**：`private_key` 中的换行符要写成 `\n`

#### Streamlit Cloud 部署
1. 登录 [Streamlit Cloud](https://share.streamlit.io/)
2. 选择你的 App → Settings → Secrets
3. 粘贴上面的 secrets.toml 内容
4. 点击 Save

### 5️⃣ 部署到 Streamlit Cloud

1. 将以下文件上传到 GitHub：
   - `tennis_life.py`
   - `requirements.txt`
2. 在 Streamlit Cloud 创建新 App
3. 选择 GitHub 仓库
4. 主文件选择 `tennis_life.py`
5. 添加 Secrets（步骤 4）
6. 点击 Deploy

---

## 📁 文件结构

```
your-repo/
├── tennis_life.py      # 主程序
├── requirements.txt    # 依赖
└── .streamlit/
    └── secrets.toml    # 本地密钥（不要上传到 GitHub！）
```

## ⚠️ 安全提示

- **永远不要**把 `secrets.toml` 或 JSON 密钥上传到 GitHub
- 在 `.gitignore` 中添加：
  ```
  .streamlit/secrets.toml
  *.json
  ```

---

## 🔧 常见问题

### Q: 显示「未连接数据库」？
A: 检查 Secrets 配置是否正确，确保服务账号有表格的编辑权限

### Q: 数据没有保存？
A: 刷新页面后点击侧边栏的「刷新数据」按钮

### Q: 如何清空数据？
A: 直接在 Google Sheets 中删除表格内容（保留第一行标题）

---

## 📞 需要帮助？

配置过程如果遇到问题，可以：
1. 检查 Google Cloud Console 的 API 是否启用
2. 确认服务账号邮箱已添加到表格共享
3. 验证 secrets.toml 格式是否正确
