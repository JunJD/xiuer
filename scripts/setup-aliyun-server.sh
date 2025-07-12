#!/bin/bash

# 小红书数据分析平台 - 阿里云服务器初始化脚本
# 使用方法: curl -fsSL https://raw.githubusercontent.com/JunJD/xiuer/main/scripts/setup-aliyun-server.sh | bash

# 不使用 set -e，允许脚本在遇到错误时继续执行
set +e

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
        
        # 特殊处理阿里云系统
        if [[ "$OS" == *"Alibaba Cloud Linux"* ]]; then
            log_info "阿里云系统详细信息:"
            log_info "- 系统ID: $ID"
            log_info "- 版本: $VERSION"
            log_info "- 基于: $ID_LIKE"
        fi
    else
        log_error "无法检测系统版本"
        exit 1
    fi
    
    # 检查系统架构
    ARCH=$(uname -m)
    log_info "系统架构: $ARCH"
    
    # 检查内存大小
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    log_info "系统内存: ${TOTAL_MEM}MB"
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt update -y
        apt upgrade -y
        apt install -y curl wget git vim htop net-tools
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Alibaba Cloud Linux"* ]] || [[ "$OS" == *"Aliyun Linux"* ]]; then
        # 阿里云系统使用yum包管理器
        yum update -y
        yum install -y curl wget git vim htop net-tools
        
        # 针对阿里云系统特殊处理EPEL仓库
        if [[ "$OS" == *"Alibaba Cloud Linux"* ]] || [[ "$OS" == *"Aliyun Linux"* ]]; then
            log_info "检测到阿里云系统，跳过EPEL安装（系统已包含类似功能）"
            # 阿里云系统通常已经包含了必要的软件包，不需要额外的EPEL
        else
            # 其他CentOS/RHEL系统安装EPEL
            yum install -y epel-release
        fi
        
        # 安装一些常用工具
        yum install -y lsof psmisc || log_warning "部分工具安装失败，继续执行"
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
    
    # 卸载旧版本（如果存在）
    echo "ℹ️ 正在卸载旧版本的 Docker..."
    sudo yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine >/dev/null 2>&1 || true

    # 针对不同系统使用不同的安装方法
    if [[ "$OS" == *"Alibaba Cloud Linux"* ]] || [[ "$OS" == *"Aliyun Linux"* ]] || [[ "$OS" == "CentOS"* ]]; then
        log_info "检测到阿里云系统或CentOS系统，使用阿里云Docker安装方法..."
        
        # 安装必要的依赖
        yum install -y yum-utils device-mapper-persistent-data lvm2
        
        # 添加阿里云Docker仓库
        yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
        
        # 清理yum缓存并安装Docker CE
        yum clean all
        yum makecache
        yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
    elif [[ "$OS" == "Ubuntu"* ]] || [[ "$OS" == "Debian"* ]]; then
        log_info "使用Docker官方安装脚本..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm -f get-docker.sh
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    fi
    
    # 启动并设置 Docker 开机自启
    echo "🚀 启动 Docker 并设置为开机自启..."
    sudo systemctl start docker
    sudo systemctl enable docker

    # 验证安装
    if command -v docker &> /dev/null; then
        echo "✅ Docker 安装成功！版本：$(docker --version)"
    else
        echo "❌ Docker 安装失败，请检查错误。"
        exit 1
    fi
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose..."
    if command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose已安装，跳过安装步骤"
        return
    fi
    # 推荐用官方二进制安装，兼容性好
    COMPOSE_VERSION="v2.29.2"
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    docker-compose version
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
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Alibaba Cloud Linux"* ]] || [[ "$OS" == *"Aliyun Linux"* ]]; then
        # CentOS/RHEL/阿里云系统使用firewalld
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
            # 如果没有firewalld，尝试使用iptables
            log_warning "Firewalld未安装，尝试配置iptables..."
            if command -v iptables &> /dev/null; then
                # 基本的iptables配置
                iptables -F
                iptables -A INPUT -i lo -j ACCEPT
                iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
                iptables -A INPUT -p tcp --dport 22 -j ACCEPT
                iptables -A INPUT -p tcp --dport 80 -j ACCEPT
                iptables -A INPUT -p tcp --dport 443 -j ACCEPT
                iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
                iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
                iptables -P INPUT DROP
                
                # 保存iptables规则
                if command -v iptables-save &> /dev/null; then
                    iptables-save > /etc/sysconfig/iptables 2>/dev/null || true
                fi
                log_success "Iptables防火墙配置完成"
            else
                log_warning "未找到防火墙工具，请手动配置安全组"
            fi
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
    
    echo "💾 正在检查并创建 Swap 交换空间..."

    # 检查是否已有 swap
    if [ "$(sudo swapon --show | wc -l)" -lt 2 ]; then
        echo "  -> 未发现活动的 Swap，正在创建 2GB 的 Swap 文件..."
        sudo fallocate -l 2G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        # 添加到 fstab 使其永久生效
        if ! grep -q "/swapfile" /etc/fstab; then
            echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
        fi
        echo "  -> Swap 创建并激活成功。"
    else
        echo "  -> 已存在 Swap，跳过创建。"
    fi

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
  "registry-mirrors": ["https://hylq3tyc.mirror.aliyuncs.com"],
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
    
    # 设置错误计数器
    ERROR_COUNT=0
    
    # 执行各个步骤，记录错误但不中断
    check_system || ((ERROR_COUNT++))
    
    update_system || {
        log_error "系统更新失败，但继续执行"
        ((ERROR_COUNT++))
    }
    
    install_docker || {
        log_error "Docker安装失败，但继续执行"
        ((ERROR_COUNT++))
    }
    
    install_docker_compose || {
        log_error "Docker Compose安装失败，但继续执行"
        ((ERROR_COUNT++))
    }
    
    configure_firewall || {
        log_warning "防火墙配置失败，请手动配置"
        ((ERROR_COUNT++))
    }
    
    create_swap || {
        log_warning "Swap配置失败，但继续执行"
        ((ERROR_COUNT++))
    }
    
    optimize_system || {
        log_warning "系统优化失败，但继续执行"
        ((ERROR_COUNT++))
    }
    
    create_app_directory || {
        log_error "应用目录创建失败"
        ((ERROR_COUNT++))
    }
    
    configure_docker || {
        log_warning "Docker配置优化失败，但继续执行"
        ((ERROR_COUNT++))
    }
    
    generate_ssh_key || {
        log_warning "SSH密钥生成失败，但继续执行"
        ((ERROR_COUNT++))
    }
    
    echo
    show_system_info
    echo
    
    # 显示错误统计
    if [[ $ERROR_COUNT -gt 0 ]]; then
        log_warning "安装过程中遇到 $ERROR_COUNT 个问题，请检查上述日志"
        log_info "大部分功能应该仍然可用，可以继续部署流程"
    else
        log_success "所有步骤都成功完成！"
    fi
    
    show_next_steps
}

# 运行主函数
main "$@" 