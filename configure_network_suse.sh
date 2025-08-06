#!/bin/bash

echo "========================================"
echo "    CONFIGURACAO DE REDE SUSE VM"
echo "========================================"
echo

# Detectar versão do SUSE
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
echo "[3/5] Verificando porta 5000..."
if command -v netstat &> /dev/null; then
    if netstat -tlnp 2>/dev/null | grep :5000; then
        echo "✅ Porta 5000 está em uso"
    else
        echo "⚠️  Porta 5000 não está em uso"
    fi
elif command -v ss &> /dev/null; then
    if ss -tlnp 2>/dev/null | grep :5000; then
        echo "✅ Porta 5000 está em uso"
    else
        echo "⚠️  Porta 5000 não está em uso"
    fi
else
    echo "⚠️  Comandos netstat/ss não encontrados"
fi

# Configurar firewall SUSE
echo "[4/5] Configurando firewall SUSE..."
if command -v firewall-cmd &> /dev/null; then
    # firewalld (SUSE Linux Enterprise 15+)
    echo "Detectado: firewalld"
    sudo firewall-cmd --permanent --add-port=5000/tcp
    sudo firewall-cmd --reload
    echo "✅ Firewall configurado (firewalld)"
    echo "Portas abertas:"
    sudo firewall-cmd --list-ports
elif command -v SuSEfirewall2 &> /dev/null; then
    # SuSEfirewall2 (SUSE Linux Enterprise 12)
    echo "Detectado: SuSEfirewall2"
    sudo SuSEfirewall2 open EXT TCP 5000
    sudo SuSEfirewall2 start
    echo "✅ Firewall configurado (SuSEfirewall2)"
elif command -v iptables &> /dev/null; then
    # iptables (fallback)
    echo "Detectado: iptables"
    sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
    echo "✅ Firewall configurado (iptables)"
else
    echo "⚠️  Nenhum firewall detectado!"
fi

# Testar conectividade
echo "[5/5] Testando conectividade..."
echo "Testando localhost..."
if command -v curl &> /dev/null; then
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
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
echo "    CONFIGURACAO DE REDE SUSE CONCLUIDA"
echo "========================================"
echo
echo "Para acessar de outras maquinas:"
echo "http://[IP-DA-VM]:5000"
echo
echo "📋 COMANDOS ÚTEIS SUSE:"
echo "  - Verificar IP: ip addr show"
echo "  - Verificar rota: ip route show"
echo "  - Verificar DNS: cat /etc/resolv.conf"
echo "  - Verificar firewall: firewall-cmd --list-all"
echo "  - Reiniciar rede: systemctl restart NetworkManager"
echo "  - Testar conectividade: curl http://localhost:5000"
echo
echo "🔧 SOLUÇÃO DE PROBLEMAS:"
echo "  - Se não conseguir acessar externamente:"
echo "    sudo firewall-cmd --permanent --add-port=5000/tcp"
echo "    sudo firewall-cmd --reload"
echo "  - Se problemas de DNS:"
echo "    sudo systemctl restart NetworkManager"
echo "  - Para verificar logs de rede:"
echo "    journalctl -u NetworkManager -f"
echo 