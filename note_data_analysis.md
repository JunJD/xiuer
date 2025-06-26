# 小红书笔记数据结构分析报告

基于实际爬取的数据，以下是小红书笔记的完整数据结构分析：

## 📊 顶层数据结构

```json
{
  "id": "笔记ID",
  "model_type": "note",
  "note_card": {...},
  "xsec_token": "安全令牌"
}
```

## 📝 note_card 核心数据结构

### 基本信息
- `type`: 笔记类型 ("normal" | "video")
- `display_title`: 笔记标题
- `id`: 笔记ID (与顶层id相同)

### 👤 用户信息 (user)
```json
{
  "user_id": "用户ID",
  "nickname": "用户昵称",
  "nick_name": "用户昵称(备选)",
  "avatar": "头像URL",
  "xsec_token": "用户安全令牌"
}
```

### 💝 互动数据 (interact_info)
```json
{
  "liked": false,           // 是否已点赞
  "liked_count": "99871",   // 点赞数(字符串)
  "collected": false,       // 是否已收藏
  "collected_count": "86361", // 收藏数(字符串)
  "comment_count": "2557",  // 评论数(字符串)
  "shared_count": "22727"   // 分享数(字符串)
}
```

### 🖼️ 封面信息 (cover)
```json
{
  "height": 2560,
  "width": 1920,
  "url_default": "高质量图片URL",
  "url_pre": "预览图片URL"
}
```

### 📸 图片列表 (image_list)
```json
[
  {
    "height": 2560,
    "width": 1920,
    "info_list": [
      {
        "image_scene": "WB_DFT",  // 默认图片
        "url": "图片URL"
      },
      {
        "image_scene": "WB_PRV",  // 预览图片
        "url": "预览图片URL"
      }
    ]
  }
]
```

### 🏷️ 角标信息 (corner_tag_info)
```json
[
  {
    "type": "publish_time",
    "text": "04-20" // 或 "8小时前"
  }
]
```

## 🆕 建议的增强字段

基于现有数据结构，建议为note model添加以下字段：

### 基础字段
- `note_type`: 笔记类型 (normal/video)
- `display_title`: 显示标题
- `cover_image`: 封面图片URL
- `cover_width`: 封面宽度
- `cover_height`: 封面高度

### 用户字段
- `author_user_id`: 作者用户ID
- `author_nickname`: 作者昵称
- `author_avatar`: 作者头像URL
- `author_xsec_token`: 作者安全令牌

### 互动字段 (转换为整数)
- `liked_count`: 点赞数
- `collected_count`: 收藏数  
- `comment_count`: 评论数
- `shared_count`: 分享数
- `is_liked`: 是否已点赞
- `is_collected`: 是否已收藏

### 图片字段
- `image_count`: 图片数量
- `image_urls`: 图片URL列表 (JSON数组)
- `preview_urls`: 预览图URL列表 (JSON数组)

### 时间字段
- `publish_time_text`: 发布时间文本 ("8小时前", "04-20")
- `publish_time_parsed`: 解析后的发布时间 (datetime)

### 技术字段
- `xsec_token`: 安全令牌
- `note_url`: 笔记完整URL

## 🎯 推荐的优先级

### 高优先级 (核心字段)
1. `note_type` - 笔记类型
2. `display_title` - 标题
3. `author_user_id` - 作者ID
4. `author_nickname` - 作者昵称
5. `liked_count`, `collected_count`, `comment_count` - 核心互动数据
6. `cover_image` - 封面图片
7. `publish_time_text` - 发布时间

### 中优先级 (增强字段)
1. `author_avatar` - 作者头像
2. `shared_count` - 分享数
3. `image_count` - 图片数量
4. `image_urls` - 图片列表
5. `cover_width`, `cover_height` - 封面尺寸

### 低优先级 (辅助字段)
1. `preview_urls` - 预览图列表
2. `is_liked`, `is_collected` - 个人状态
3. `author_xsec_token` - 作者令牌
4. `publish_time_parsed` - 解析时间

## 💡 数据处理建议

### 数字字段处理
```python
# 互动数据需要从字符串转换为整数
liked_count = int(interact_info.get("liked_count", "0") or "0")
```

### 时间字段处理
```python
# 发布时间解析
def parse_publish_time(time_text):
    if "小时前" in time_text:
        hours = int(time_text.replace("小时前", ""))
        return datetime.now() - timedelta(hours=hours)
    elif "分钟前" in time_text:
        minutes = int(time_text.replace("分钟前", ""))
        return datetime.now() - timedelta(minutes=minutes)
    elif re.match(r"\d{2}-\d{2}", time_text):  # MM-DD格式
        month, day = time_text.split("-")
        return datetime(datetime.now().year, int(month), int(day))
```

### 图片URL提取
```python
# 提取所有WB_DFT类型的图片URL
image_urls = []
for image in note_card.get("image_list", []):
    for info in image.get("info_list", []):
        if info.get("image_scene") == "WB_DFT":
            image_urls.append(info["url"])
            break
```

## 🔄 与现有Schema的映射

当前使用的字段 → 建议的新字段：
- `title` → `display_title`
- `author.nickname` → `author_nickname`
- `interact_info.liked_count` → `liked_count` (转整数)
- `image_list` → `image_urls` (提取URL列表)

这样的数据结构将为后续的数据分析、搜索和展示提供更丰富的信息支持。 