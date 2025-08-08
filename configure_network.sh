#!/bin/bash

echo "========================================"
echo "    CONFIGURACAO DE REDE VM LINUX"
echo "========================================"
echo

# Detectar distribuição Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "Sistema detectado: $PRETTY_NAME"
    echo "Versão: $VERSION"
    echo
fi

# Obter IP da VM
echo "[1/5] Obtendo IP da VM..."
if command -v ip &> /dev/null; then
    echo "IPs encontrados:"
    ip addr show | grep -E "inet.*global" | awk '{print "  " $2}'
else
    echo "⚠️  Comando 'ip' não encontrado"
fi

# Verificar hostname
echo "[2/5] Verificando hostname..."
echo "Hostname: $(hostname)"
echo "FQDN: $(hostname -f 2>/dev/null || echo 'N/A')"

# Verificar porta 5000
echo "[3/5] Verificando porta 80..."
if command -v netstat &> /dev/null; then
    if netstat -tlnp 2>/dev/null | grep :80; then
        echo "✅ Porta 80 está em uso"
    else
        echo "⚠️  Porta 80 não está em uso"
    fi
elif command -v ss &> /dev/null; then
    if ss -tlnp 2>/dev/null | grep :80; then
        echo "✅ Porta 80 está em uso"
    else
        echo "⚠️  Porta 80 não está em uso"
    fi
else
    echo "⚠️  Comandos netstat/ss não encontrados"
fi

# Configurar firewall baseado na distribuição
echo "[4/5] Configurando firewall..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    case $ID in
        "ubuntu"|"debian")
            if command -v ufw &> /dev/null; then
                sudo ufw allow 80
                echo "✅ Firewall UFW configurado"
            else
                echo "⚠️  UFW não encontrado"
            fi
            ;;
        "opensuse"|"sles"|"suse")
            if command -v firewall-cmd &> /dev/null; then
                sudo firewall-cmd --permanent --add-port=80/tcp
                sudo firewall-cmd --reload
                echo "✅ Firewall firewalld configurado"
            elif command -v SuSEfirewall2 &> /dev/null; then
                sudo SuSEfirewall2 open EXT TCP 80
                sudo SuSEfirewall2 start
                echo "✅ Firewall SuSEfirewall2 configurado"
            else
                echo "⚠️  Firewall não encontrado"
            fi
            ;;
        "centos"|"rhel"|"fedora")
            if command -v firewall-cmd &> /dev/null; then
                sudo firewall-cmd --permanent --add-port=80/tcp
                sudo firewall-cmd --reload
                echo "✅ Firewall firewalld configurado"
            else
                echo "⚠️  Firewall não encontrado"
            fi
            ;;
        *)
            echo "⚠️  Distribuição não suportada: $ID"
            ;;
    esac
fi

# Testar conectividade
echo "[5/5] Testando conectividade..."
echo "Testando localhost..."
if command -v curl &> /dev/null; then
    if curl -s http://localhost > /dev/null 2>&1; then
        echo "✅ Localhost: OK"
    else
        echo "⚠️  Localhost: FALHOU (aplicação não está rodando)"
    fi
else
    echo "⚠️  curl não encontrado para teste de conectividade"
fi

# Verificar serviços de rede
echo
echo "Verificando serviços de rede..."
if command -v systemctl &> /dev/null; then
    echo "Status do NetworkManager:"
    systemctl is-active NetworkManager 2>/dev/null || echo "  NetworkManager não encontrado"
    
    echo "Status do wicked (SUSE):"
    systemctl is-active wicked 2>/dev/null || echo "  wicked não encontrado"
    
    echo "Status do network:"
    systemctl is-active network 2>/dev/null || echo "  network não encontrado"
fi

echo
echo "========================================"
echo "    CONFIGURACAO DE REDE CONCLUIDA"
echo "========================================"
echo
echo "Para acessar de outras maquinas:"
echo "http://[IP-DA-VM]"
echo
echo "📋 COMANDOS ÚTEIS:"
echo "  - Verificar IP: ip addr show"
echo "  - Verificar rota: ip route show"
echo "  - Verificar DNS: cat /etc/resolv.conf"
echo "  - Testar conectividade: curl http://localhost"
echo
echo "🔧 SOLUÇÃO DE PROBLEMAS:"
echo "  - Se não conseguir acessar externamente, configure o firewall:"
echo "    Ubuntu/Debian: sudo ufw allow 80"
echo "    SUSE/Red Hat: sudo firewall-cmd --permanent --add-port=80/tcp"
echo "  - Se problemas de DNS: sudo systemctl restart NetworkManager"
echo "  - Para verificar logs: journalctl -u NetworkManager -f"
echo 