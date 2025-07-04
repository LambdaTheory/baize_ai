# 白泽AI - 分发说明

## 打包方式

### 1. 创建.app应用包
```bash
python3 build_mac.py
```

### 2. 创建DMG安装包（推荐）
```bash
python3 build_mac.py --create-dmg
```

## 分发选项对比

### DMG安装包（推荐）
**优点：**
- ✅ 专业的macOS应用分发格式
- ✅ 包含拖拽安装界面（应用 → Applications文件夹）
- ✅ 包含详细的安装和使用说明
- ✅ 用户体验更好，安装过程清晰
- ✅ 文件完整性校验
- ✅ 压缩存储，节省下载时间

**缺点：**
- ❌ 文件稍大（~177MB）
- ❌ 仍需处理安全警告

### 直接.app文件
**优点：**
- ✅ 文件较小（~225MB未压缩）
- ✅ 可以直接运行，无需安装

**缺点：**
- ❌ 不够专业
- ❌ 用户可能不知道如何正确"安装"
- ❌ 缺少使用说明

## 安全警告问题

### 问题说明
无论使用DMG还是直接分发.app，未签名的应用都会触发macOS的安全警告：
- "无法打开，因为无法验证开发者"
- 需要在系统偏好设置中手动允许

### 解决方案

#### 1. 用户手动允许（当前方案）
用户需要：
1. 尝试打开应用
2. 在系统偏好设置 > 安全性与隐私 > 通用中点击"仍要打开"
3. 或使用终端命令移除隔离属性

#### 2. 代码签名（推荐但需要成本）
```bash
# 需要Apple Developer账号（$99/年）
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" 白泽.app
```

#### 3. 公证（Notarization）
```bash
# 需要Apple Developer账号，提交给Apple审核
xcrun notarytool submit 白泽.dmg --keychain-profile "notarytool-password"
```

## 推荐分发策略

### 当前阶段（无签名）
1. **使用DMG格式分发**
2. **提供详细的安装说明**
3. **在README中说明安全警告的处理方法**

### 未来改进（有预算时）
1. **购买Apple Developer账号**
2. **对应用进行代码签名**
3. **提交公证以消除安全警告**

## 用户安装流程

### 使用DMG安装包
1. 下载 `白泽.dmg` 文件
2. 双击挂载DMG
3. 将 `白泽.app` 拖拽到 `Applications` 文件夹
4. 在Launchpad中找到并启动应用
5. 如遇安全警告，按照说明文件处理

### 直接使用.app文件
1. 下载并解压 `白泽.app`
2. 双击启动（或移动到Applications文件夹）
3. 如遇安全警告，在系统偏好设置中允许

## 文件结构

```
dist/
├── 白泽.app          # macOS应用包
├── 白泽.dmg          # DMG安装包（推荐分发）
└── 白泽/             # PyInstaller构建目录
```

## 数据存储

用户数据自动保存在：
```
~/Library/Application Support/白泽AI/
├── database/
│   └── records.db    # 图片记录数据库
└── data/
    └── prompt_history.json  # 提示词历史
```

## 总结

**推荐使用DMG格式分发**，因为：
1. 更专业的用户体验
2. 包含完整的安装指导
3. 符合macOS应用分发标准
4. 用户更容易理解和使用

安全警告问题在未签名应用中无法避免，但通过清晰的说明文档可以帮助用户正确处理。
