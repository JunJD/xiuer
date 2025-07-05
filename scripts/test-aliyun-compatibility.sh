#!/bin/bash

# 阿里云系统兼容性测试脚本

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

echo "========================================"
echo "阿里云系统兼容性测试"
echo "========================================"

# 检测系统信息
log_info "检测系统信息..."
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    echo "系统名称: $NAME"
    echo "版本: $VERSION"
    echo "ID: $ID"
    echo "基于: $ID_LIKE"
    
    if [[ "$NAME" == *"Alibaba Cloud Linux"* ]]; then
        log_success "检测到阿里云系统"
        SYSTEM_TYPE="aliyun"
    elif [[ "$NAME" == *"CentOS"* ]]; then
        log_success "检测到CentOS系统"
        SYSTEM_TYPE="centos"
    elif [[ "$NAME" == *"Ubuntu"* ]]; then
        log_success "检测到Ubuntu系统"
        SYSTEM_TYPE="ubuntu"
    else
        log_warning "未知系统类型: $NAME"
        SYSTEM_TYPE="unknown"
    fi
else
    log_error "无法读取系统信息"
    exit 1
fi

# 检测包管理器
log_info "检测包管理器..."
if command -v yum &> /dev/null; then
    log_success "找到yum包管理器"
    PKG_MANAGER="yum"
elif command -v apt &> /dev/null; then
    log_success "找到apt包管理器"
    PKG_MANAGER="apt"
else
    log_error "未找到支持的包管理器"
    exit 1
fi

# 检测防火墙工具
log_info "检测防火墙工具..."
if command -v firewall-cmd &> /dev/null; then
    log_success "找到firewalld"
    FIREWALL="firewalld"
elif command -v ufw &> /dev/null; then
    log_success "找到ufw"
    FIREWALL="ufw"
elif command -v iptables &> /dev/null; then
    log_success "找到iptables"
    FIREWALL="iptables"
else
    log_warning "未找到防火墙工具"
    FIREWALL="none"
fi

# 检测Docker
log_info "检测Docker..."
if command -v docker &> /dev/null; then
    log_success "Docker已安装: $(docker --version)"
    DOCKER_INSTALLED="yes"
else
    log_info "Docker未安装"
    DOCKER_INSTALLED="no"
fi

# 检测Docker Compose
log_info "检测Docker Compose..."
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose已安装: $(docker-compose --version)"
    COMPOSE_INSTALLED="yes"
else
    log_info "Docker Compose未安装"
    COMPOSE_INSTALLED="no"
fi

# 检测内存和Swap
log_info "检测内存和Swap..."
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
SWAP_COUNT=$(swapon --show | wc -l)
echo "总内存: ${TOTAL_MEM}MB"
echo "Swap分区数: $SWAP_COUNT"

# 测试网络连接
log_info "测试网络连接..."
if curl -s --connect-timeout 5 https://mirrors.aliyun.com > /dev/null; then
    log_success "阿里云镜像源连接正常"
    ALIYUN_NETWORK="ok"
else
    log_warning "阿里云镜像源连接失败"
    ALIYUN_NETWORK="fail"
fi

if curl -s --connect-timeout 5 https://get.docker.com > /dev/null; then
    log_success "Docker官方源连接正常"
    DOCKER_NETWORK="ok"
else
    log_warning "Docker官方源连接失败"
    DOCKER_NETWORK="fail"
fi

# 输出兼容性报告
echo
echo "========================================"
echo "兼容性测试报告"
echo "========================================"
echo "系统类型: $SYSTEM_TYPE"
echo "包管理器: $PKG_MANAGER"
echo "防火墙工具: $FIREWALL"
echo "Docker状态: $DOCKER_INSTALLED"
echo "Docker Compose状态: $COMPOSE_INSTALLED"
echo "内存大小: ${TOTAL_MEM}MB"
echo "Swap状态: $SWAP_COUNT个分区"
echo "阿里云网络: $ALIYUN_NETWORK"
echo "Docker网络: $DOCKER_NETWORK"

# 给出建议
echo
echo "========================================"
echo "建议"
echo "========================================"

if [[ "$SYSTEM_TYPE" == "aliyun" ]]; then
    log_success "系统兼容性良好，可以使用阿里云优化的安装方法"
    if [[ "$ALIYUN_NETWORK" == "ok" ]]; then
        echo "建议使用阿里云镜像源安装Docker"
    fi
elif [[ "$SYSTEM_TYPE" == "centos" ]]; then
    log_success "CentOS系统兼容性良好"
elif [[ "$SYSTEM_TYPE" == "ubuntu" ]]; then
    log_success "Ubuntu系统兼容性良好"
else
    log_warning "系统兼容性未知，可能需要手动调整"
fi

if [[ $TOTAL_MEM -le 2048 ]]; then
    log_info "内存较小，建议创建Swap文件"
fi

if [[ "$DOCKER_INSTALLED" == "no" ]]; then
    log_info "需要安装Docker"
fi

if [[ "$COMPOSE_INSTALLED" == "no" ]]; then
    log_info "需要安装Docker Compose"
fi

echo
log_info "测试完成！现在可以运行完整的初始化脚本" 