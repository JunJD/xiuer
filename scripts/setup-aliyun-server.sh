#!/bin/bash

# 小红书数据分析平台 - 阿里云服务器初始化脚本
# 使用方法: curl -fsSL https://raw.githubusercontent.com/JunJD/xiuer/main/scripts/setup-aliyun-server.sh | bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查是否为root用户
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    # 检查系统版本
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        log_info "检测到系统: $OS $VER"
    else
        log_error "无法检测系统版本"
        exit 1
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt update -y
        apt upgrade -y
        apt install -y curl wget git vim htop net-tools
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        yum update -y
        yum install -y curl wget git vim htop net-tools
    else
        log_error "不支持的操作系统: $OS"
        exit 1
    fi
    
    log_success "系统更新完成"
}

# 安装Docker
install_docker() {
    log_info "安装Docker..."
    
    # 检查Docker是否已安装
    if command -v docker &> /dev/null; then
        log_warning "Docker已安装，跳过安装步骤"
        return
    fi
    
    # 使用官方安装脚本
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    # 验证安装
    if docker --version &> /dev/null; then
        log_success "Docker安装成功: $(docker --version)"
    else
        log_error "Docker安装失败"
        exit 1
    fi
    
    # 清理安装文件
    rm -f get-docker.sh
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose..."
    
    # 检查Docker Compose是否已安装
    if command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose已安装，跳过安装步骤"
        return
    fi
    
    # 下载Docker Compose
    DOCKER_COMPOSE_VERSION="v2.24.0"
    curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    chmod +x /usr/local/bin/docker-compose
    
    # 验证安装
    if docker-compose --version &> /dev/null; then
        log_success "Docker Compose安装成功: $(docker-compose --version)"
    else
        log_error "Docker Compose安装失败"
        exit 1
    fi
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        # Ubuntu/Debian使用ufw
        if command -v ufw &> /dev/null; then
            ufw --force reset
            ufw default deny incoming
            ufw default allow outgoing
            ufw allow ssh
            ufw allow 22/tcp
            ufw allow 80/tcp
            ufw allow 443/tcp
            ufw allow 3000/tcp
            ufw allow 8000/tcp
            ufw --force enable
            log_success "UFW防火墙配置完成"
        else
            log_warning "UFW未安装，跳过防火墙配置"
        fi
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        # CentOS/RHEL使用firewalld
        if command -v firewall-cmd &> /dev/null; then
            systemctl start firewalld
            systemctl enable firewalld
            firewall-cmd --permanent --add-port=22/tcp
            firewall-cmd --permanent --add-port=80/tcp
            firewall-cmd --permanent --add-port=443/tcp
            firewall-cmd --permanent --add-port=3000/tcp
            firewall-cmd --permanent --add-port=8000/tcp
            firewall-cmd --reload
            log_success "Firewalld防火墙配置完成"
        else
            log_warning "Firewalld未安装，跳过防火墙配置"
        fi
    fi
}

# 创建Swap文件
create_swap() {
    log_info "检查内存和Swap配置..."
    
    # 检查当前内存
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    log_info "系统总内存: ${TOTAL_MEM}MB"
    
    # 检查是否已有Swap
    if [[ $(swapon --show | wc -l) -gt 0 ]]; then
        log_warning "Swap已存在，跳过创建"
        swapon --show
        return
    fi
    
    # 为2GB内存的服务器创建2GB Swap
    if [[ $TOTAL_MEM -le 2048 ]]; then
        log_info "内存较小，创建2GB Swap文件..."
        
        # 创建Swap文件
        fallocate -l 2G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        
        # 永久启用Swap
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
        
        # 调整Swap使用策略
        echo 'vm.swappiness=10' >> /etc/sysctl.conf
        echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
        
        log_success "Swap创建完成"
        free -h
    else
        log_info "内存充足，跳过Swap创建"
    fi
}

# 优化系统配置
optimize_system() {
    log_info "优化系统配置..."
    
    # 增加文件描述符限制
    cat >> /etc/security/limits.conf << EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
EOF
    
    # 优化网络配置
    cat >> /etc/sysctl.conf << EOF
# 网络优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr
EOF
    
    # 应用配置
    sysctl -p
    
    log_success "系统优化完成"
}

# 创建应用目录
create_app_directory() {
    log_info "创建应用目录..."
    
    mkdir -p /app/xiuer
    chmod 755 /app/xiuer
    
    log_success "应用目录创建完成: /app/xiuer"
}

# 配置Docker优化
configure_docker() {
    log_info "配置Docker优化..."
    
    # 创建Docker配置文件
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  },
  "storage-driver": "overlay2"
}
EOF
    
    # 重启Docker服务
    systemctl restart docker
    
    log_success "Docker配置优化完成"
}

# 生成SSH密钥（可选）
generate_ssh_key() {
    log_info "检查SSH密钥..."
    
    if [[ -f ~/.ssh/id_rsa ]]; then
        log_warning "SSH密钥已存在，跳过生成"
        return
    fi
    
    read -p "是否生成新的SSH密钥? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
        log_success "SSH密钥生成完成"
        log_info "公钥内容:"
        cat ~/.ssh/id_rsa.pub
    fi
}

# 显示系统信息
show_system_info() {
    log_info "系统信息总结:"
    echo "=================================="
    echo "操作系统: $OS $VER"
    echo "内存使用: $(free -h | awk 'NR==2{printf "%.1f/%.1fGB (%.1f%%)", $3/1024, $2/1024, $3*100/$2}')"
    echo "磁盘使用: $(df -h / | awk 'NR==2{printf "%s/%s (%s)", $3, $2, $5}')"
    echo "Docker版本: $(docker --version 2>/dev/null || echo '未安装')"
    echo "Docker Compose版本: $(docker-compose --version 2>/dev/null || echo '未安装')"
    echo "Swap状态: $(swapon --show | wc -l)个Swap分区"
    echo "应用目录: /app/xiuer"
    echo "=================================="
}

# 显示后续步骤
show_next_steps() {
    log_success "🎉 阿里云服务器初始化完成！"
    echo
    log_info "后续步骤："
    echo "1. 在GitHub仓库中配置Secrets（参考docs/aliyun-deployment.md）"
    echo "2. 推送代码到main分支触发自动部署"
    echo "3. 或者手动运行GitHub Actions工作流"
    echo
    log_info "有用的命令："
    echo "• 查看系统状态: htop"
    echo "• 查看Docker状态: docker ps"
    echo "• 查看应用日志: cd /app/xiuer && docker-compose logs -f"
    echo "• 重启Docker: systemctl restart docker"
    echo
    log_info "访问地址（部署完成后）："
    echo "• 前端: http://$(curl -s ifconfig.me)"
    echo "• 后端API: http://$(curl -s ifconfig.me)/docs"
}

# 主函数
main() {
    echo "========================================"
    echo "小红书数据分析平台 - 阿里云服务器初始化"
    echo "========================================"
    echo
    
    check_system
    update_system
    install_docker
    install_docker_compose
    configure_firewall
    create_swap
    optimize_system
    create_app_directory
    configure_docker
    generate_ssh_key
    
    echo
    show_system_info
    echo
    show_next_steps
}

# 运行主函数
main "$@" 