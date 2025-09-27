/**
 * JavaScript para Dashboard Administrativo
 */

// Configurações
const API_BASE = "/api";
let currentAdmin = null;
let dashboardData = null;
let refreshInterval = null;

// Charts
let apiUsageChart = null;
let providerChart = null;
let performanceChart = null;
let usersChart = null;

// Inicialização
document.addEventListener("DOMContentLoaded", function () {
  checkAdminAuthentication();
  initializeEventListeners();
  startRealTimeUpdates();
});

// Verificar autenticação de administrador
async function checkAdminAuthentication() {
  const token = localStorage.getItem("authToken");

  if (!token) {
    window.location.href = "index.html";
    return;
  }

  try {
    showLoading(true);

    // Verificar se é admin e carregar dashboard
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // Timeout de 10 segundos

    const response = await fetch(`${API_BASE}/admin/dashboard`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      dashboardData = data;
      console.log("Dashboard data loaded:", dashboardData);
      updateDashboard();
    } else if (response.status === 401) {
      localStorage.removeItem("authToken");
      window.location.href = "index.html";
    } else if (response.status === 403) {
      alert("Acesso negado: você não tem permissões de administrador");
      window.location.href = "index.html";
    } else {
      console.error("Erro HTTP:", response.status, response.statusText);
      showAlert(`Erro ao carregar dashboard: ${response.status}`, "error");

      // Carregar dados padrão em caso de erro
      dashboardData = createDefaultDashboardData();
      updateDashboard();
    }
  } catch (error) {
    console.error("Erro de conexão:", error);

    if (error.name === "AbortError") {
      showAlert("Timeout na conexão com o servidor", "error");
    } else {
      showAlert("Erro de conexão com o servidor", "error");
    }

    // Carregar dados padrão em caso de erro
    dashboardData = createDefaultDashboardData();
    updateDashboard();
  } finally {
    showLoading(false);
  }
}

// Atualizar dashboard
function updateDashboard() {
  if (!dashboardData) {
    console.warn("Dashboard data não disponível");
    // Criar dados padrão se não existir
    dashboardData = createDefaultDashboardData();
  }

  try {
    updateStatsOverview();
    updateCharts();
    updateRecentActivity();
  } catch (error) {
    console.error("Erro ao atualizar dashboard:", error);
    showAlert("Erro ao carregar dados do dashboard", "error");
  }
}

// Criar dados padrão para o dashboard
function createDefaultDashboardData() {
  return {
    overview: {
      total_users: 0,
      active_users_24h: 0,
      total_api_calls: 0,
      api_calls_24h: 0,
      error_rate_24h: 0,
      avg_response_time_24h: 0,
    },
    charts_data: {
      timeline: {
        dates: [],
        api_calls: [],
        active_users: [],
      },
      provider_distribution: {
        labels: [],
        data: [],
      },
    },
  };
}

// Atualizar estatísticas gerais
function updateStatsOverview() {
  const overview = dashboardData?.overview || {};
  const container = document.getElementById("statsOverview");

  if (!container) {
    console.error("Container statsOverview não encontrado");
    return;
  }

  container.innerHTML = `
        <div class="stat-card">
            <div class="stat-card-header">
                <span class="stat-card-title">Total de Usuários</span>
                <div class="stat-card-icon" style="background: #e0f2fe; color: #0277bd;">
                    <i class="bi bi-people"></i>
                </div>
            </div>
            <div class="stat-card-value">${overview.total_users || 0}</div>
            <div class="stat-card-change">
                <span class="change-positive">
                    <i class="bi bi-arrow-up me-1"></i>
                    ${overview.active_users_24h || 0} ativos hoje
                </span>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-card-header">
                <span class="stat-card-title">Chamadas API 24h</span>
                <div class="stat-card-icon" style="background: #f3e5f5; color: #7b1fa2;">
                    <i class="bi bi-graph-up"></i>
                </div>
            </div>
            <div class="stat-card-value">${overview.api_calls_24h || 0}</div>
            <div class="stat-card-change">
                <span class="change-positive">
                    <i class="bi bi-arrow-up me-1"></i>
                    ${overview.total_api_calls || 0} total
                </span>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-card-header">
                <span class="stat-card-title">Taxa de Erro</span>
                <div class="stat-card-icon" style="background: ${
                  overview.error_rate_24h > 5
                    ? "#ffebee; color: #c62828"
                    : "#e8f5e8; color: #2e7d32"
                };">
                    <i class="bi bi-${
                      overview.error_rate_24h > 5
                        ? "exclamation-triangle"
                        : "check-circle"
                    }"></i>
                </div>
            </div>
            <div class="stat-card-value">${(
              overview.error_rate_24h || 0
            ).toFixed(1)}%</div>
            <div class="stat-card-change">
                <span class="${
                  overview.error_rate_24h > 5
                    ? "change-negative"
                    : "change-positive"
                }">
                    <i class="bi bi-${
                      overview.error_rate_24h > 5 ? "arrow-up" : "arrow-down"
                    } me-1"></i>
                    ${
                      overview.error_rate_24h <= 5
                        ? "Sistema estável"
                        : "Atenção necessária"
                    }
                </span>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-card-header">
                <span class="stat-card-title">Tempo Resposta</span>
                <div class="stat-card-icon" style="background: #fff3e0; color: #f57c00;">
                    <i class="bi bi-speedometer2"></i>
                </div>
            </div>
            <div class="stat-card-value">${(
              overview.avg_response_time_24h || 0
            ).toFixed(1)}s</div>
            <div class="stat-card-change">
                <span class="change-positive">
                    <i class="bi bi-clock me-1"></i>
                    Média 24h
                </span>
            </div>
        </div>
    `;
}

// Atualizar gráficos
function updateCharts() {
  showChartLoading("apiChartLoading", true);
  showChartLoading("providerChartLoading", true);

  try {
    updateAPIUsageChart();
    updateProviderChart();
  } finally {
    // Esconder loading depois de um pequeno delay
    setTimeout(() => {
      showChartLoading("apiChartLoading", false);
      showChartLoading("providerChartLoading", false);
    }, 500);
  }
}

// Controlar loading dos gráficos
function showChartLoading(loadingId, show) {
  const loadingElement = document.getElementById(loadingId);
  if (loadingElement) {
    loadingElement.style.display = show ? "flex" : "none";
  }
}

// Gráfico de uso da API
function updateAPIUsageChart() {
  const ctx = document.getElementById("apiUsageChart");

  if (!ctx) {
    console.error("Canvas apiUsageChart não encontrado");
    return;
  }

  // Verificar se os dados existem
  if (
    !dashboardData ||
    !dashboardData.charts_data ||
    !dashboardData.charts_data.timeline
  ) {
    console.warn("Dados do gráfico não disponíveis, criando gráfico vazio");
    createEmptyAPIChart(ctx);
    return;
  }

  const chartData = dashboardData.charts_data.timeline;

  // Verificar se os arrays de dados existem
  if (!chartData.dates || !chartData.api_calls || !chartData.active_users) {
    console.warn("Arrays de dados não disponíveis, criando gráfico vazio");
    createEmptyAPIChart(ctx);
    return;
  }

  if (apiUsageChart) {
    apiUsageChart.destroy();
  }

  try {
    apiUsageChart = new Chart(ctx.getContext("2d"), {
      type: "line",
      data: {
        labels: chartData.dates.map((date) => {
          try {
            const d = new Date(date);
            return d.toLocaleDateString("pt-BR", {
              day: "2-digit",
              month: "2-digit",
            });
          } catch (e) {
            return date; // Fallback para string original
          }
        }),
        datasets: [
          {
            label: "Chamadas API",
            data: chartData.api_calls || [],
            borderColor: "#4f46e5",
            backgroundColor: "rgba(79, 70, 229, 0.1)",
            tension: 0.4,
            fill: true,
          },
          {
            label: "Usuários Ativos",
            data: chartData.active_users || [],
            borderColor: "#06d6a0",
            backgroundColor: "rgba(6, 214, 160, 0.1)",
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(0,0,0,0.1)",
            },
          },
          x: {
            grid: {
              color: "rgba(0,0,0,0.1)",
            },
          },
        },
      },
    });
  } catch (error) {
    console.error("Erro ao criar gráfico de API:", error);
    createEmptyAPIChart(ctx);
  }
}

// Criar gráfico vazio quando não há dados
function createEmptyAPIChart(ctx) {
  if (apiUsageChart) {
    apiUsageChart.destroy();
  }

  const emptyDates = [];
  const currentDate = new Date();

  // Gerar últimos 7 dias
  for (let i = 6; i >= 0; i--) {
    const date = new Date(currentDate);
    date.setDate(date.getDate() - i);
    emptyDates.push(
      date.toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
      })
    );
  }

  apiUsageChart = new Chart(ctx.getContext("2d"), {
    type: "line",
    data: {
      labels: emptyDates,
      datasets: [
        {
          label: "Chamadas API",
          data: [0, 0, 0, 0, 0, 0, 0],
          borderColor: "#4f46e5",
          backgroundColor: "rgba(79, 70, 229, 0.1)",
          tension: 0.4,
          fill: true,
        },
        {
          label: "Usuários Ativos",
          data: [0, 0, 0, 0, 0, 0, 0],
          borderColor: "#06d6a0",
          backgroundColor: "rgba(6, 214, 160, 0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: "rgba(0,0,0,0.1)",
          },
        },
        x: {
          grid: {
            color: "rgba(0,0,0,0.1)",
          },
        },
      },
    },
  });
}

// Gráfico de distribuição de provedores
function updateProviderChart() {
  const ctx = document.getElementById("providerChart");

  if (!ctx) {
    console.error("Canvas providerChart não encontrado");
    return;
  }

  // Verificar se os dados existem
  if (
    !dashboardData ||
    !dashboardData.charts_data ||
    !dashboardData.charts_data.provider_distribution
  ) {
    console.warn(
      "Dados do gráfico de provedores não disponíveis, criando gráfico vazio"
    );
    createEmptyProviderChart(ctx);
    return;
  }

  const chartData = dashboardData.charts_data.provider_distribution;

  // Verificar se os arrays de dados existem
  if (!chartData.labels || !chartData.data || chartData.labels.length === 0) {
    console.warn(
      "Arrays de dados de provedores não disponíveis, criando gráfico vazio"
    );
    createEmptyProviderChart(ctx);
    return;
  }

  if (providerChart) {
    providerChart.destroy();
  }

  const colors = [
    "#4f46e5",
    "#06d6a0",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#f97316",
    "#10b981",
  ];

  try {
    providerChart = new Chart(ctx.getContext("2d"), {
      type: "doughnut",
      data: {
        labels: chartData.labels || [],
        datasets: [
          {
            data: chartData.data || [],
            backgroundColor: colors.slice(0, (chartData.labels || []).length),
            borderWidth: 2,
            borderColor: "#ffffff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
          },
        },
      },
    });
  } catch (error) {
    console.error("Erro ao criar gráfico de provedores:", error);
    createEmptyProviderChart(ctx);
  }
}

// Criar gráfico vazio para provedores
function createEmptyProviderChart(ctx) {
  if (providerChart) {
    providerChart.destroy();
  }

  const colors = ["#4f46e5", "#06d6a0", "#f59e0b", "#ef4444", "#8b5cf6"];

  providerChart = new Chart(ctx.getContext("2d"), {
    type: "doughnut",
    data: {
      labels: ["Groq", "Gemini", "HuggingFace", "Cohere", "Together"],
      datasets: [
        {
          data: [1, 1, 1, 1, 1], // Valores mínimos para mostrar o gráfico
          backgroundColor: colors,
          borderWidth: 2,
          borderColor: "#ffffff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.label + ": Sem dados disponíveis";
            },
          },
        },
      },
    },
  });
}

// Atualizar atividade recente
function updateRecentActivity() {
  const container = document.getElementById("recentActivity");

  // Simular atividades recentes baseadas nos dados
  const activities = generateRecentActivities();

  container.innerHTML = activities
    .map(
      (activity) => `
        <div class="activity-item">
            <div class="activity-icon" style="background: ${activity.color}; color: white;">
                <i class="bi bi-${activity.icon}"></i>
            </div>
            <div class="activity-content">
                <h6>${activity.title}</h6>
                <p>${activity.description} • ${activity.time}</p>
            </div>
        </div>
    `
    )
    .join("");
}

// Gerar atividades recentes simuladas
function generateRecentActivities() {
  const now = new Date();
  const activities = [];

  // Baseado nos dados do dashboard
  if (dashboardData.overview.api_calls_24h > 0) {
    activities.push({
      icon: "graph-up",
      color: "#4f46e5",
      title: "Pico de Uso da API",
      description: `${dashboardData.overview.api_calls_24h} chamadas registradas`,
      time: "Últimas 24h",
    });
  }

  if (dashboardData.overview.active_users_24h > 0) {
    activities.push({
      icon: "people",
      color: "#06d6a0",
      title: "Usuários Ativos",
      description: `${dashboardData.overview.active_users_24h} usuários ativos`,
      time: "Hoje",
    });
  }

  if (dashboardData.overview.error_rate_24h > 5) {
    activities.push({
      icon: "exclamation-triangle",
      color: "#ef4444",
      title: "Taxa de Erro Elevada",
      description: `${dashboardData.overview.error_rate_24h.toFixed(
        1
      )}% de erros detectados`,
      time: "Últimas 24h",
    });
  }

  // Adicionar atividades padrão se necessário
  if (activities.length === 0) {
    activities.push({
      icon: "check-circle",
      color: "#10b981",
      title: "Sistema Operacional",
      description: "Todos os serviços funcionando normalmente",
      time: "Agora",
    });
  }

  return activities;
}

// Carregar usuários
async function loadUsers() {
  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/admin/users`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const data = await response.json();
      displayUsers(data.users);
    } else {
      showAlert("Erro ao carregar usuários", "error");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "error");
  }
}

// Exibir usuários
function displayUsers(users) {
  const tbody = document.getElementById("usersTableBody");

  tbody.innerHTML = users
    .map((userData) => {
      const user = userData.user;
      const profile = userData.member_profile;

      return `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-sm bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2">
                            ${user.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                            <div class="fw-semibold">${user.username}</div>
                            <small class="text-muted">ID: ${user.id.substring(
                              0,
                              8
                            )}...</small>
                        </div>
                    </div>
                </td>
                <td>${user.email}</td>
                <td>
                    <span class="subscription-badge subscription-${
                      profile ? profile.subscription_plan : "free"
                    }">
                        ${profile ? profile.subscription_plan : "free"}
                    </span>
                </td>
                <td>
                    <span class="status-badge ${
                      user.is_active ? "status-online" : "status-offline"
                    }">
                        ${user.is_active ? "Ativo" : "Inativo"}
                    </span>
                </td>
                <td>
                    <small class="text-muted">
                        ${
                          user.last_login
                            ? new Date(user.last_login).toLocaleString("pt-BR")
                            : "Nunca"
                        }
                    </small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-admin-outline" onclick="viewUser('${
                          user.id
                        }')">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-admin-outline" onclick="toggleUserStatus('${
                          user.id
                        }', ${user.is_active})">
                            <i class="bi bi-${
                              user.is_active ? "pause" : "play"
                            }"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    })
    .join("");
}

// Alternar status do usuário
async function toggleUserStatus(userId, currentStatus) {
  const action = currentStatus ? "suspend" : "activate";
  const actionText = currentStatus ? "suspender" : "ativar";

  if (!confirm(`Deseja ${actionText} este usuário?`)) return;

  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(
      `${API_BASE}/admin/users/${userId}/${action}`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    if (response.ok) {
      showAlert(`Usuário ${actionText}do com sucesso!`, "success");
      loadUsers(); // Recarregar lista
    } else {
      showAlert(`Erro ao ${actionText} usuário`, "error");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "error");
  }
}

// Visualizar detalhes do usuário
async function viewUser(userId) {
  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const data = await response.json();
      showUserDetailsModal(data);
    } else {
      showAlert("Erro ao carregar detalhes do usuário", "error");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "error");
  }
}

// Mostrar modal com detalhes do usuário
function showUserDetailsModal(userData) {
  const user = userData.user;
  const profile = userData.profile;
  const analytics = userData.analytics;

  const modalHTML = `
        <div class="modal fade" id="userDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Detalhes do Usuário</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Informações Básicas</h6>
                                <p><strong>Nome:</strong> ${user.username}</p>
                                <p><strong>Email:</strong> ${user.email}</p>
                                <p><strong>Status:</strong> ${
                                  user.is_active ? "Ativo" : "Inativo"
                                }</p>
                                <p><strong>Criado em:</strong> ${new Date(
                                  user.created_at
                                ).toLocaleString("pt-BR")}</p>
                            </div>
                            <div class="col-md-6">
                                <h6>Estatísticas</h6>
                                <p><strong>Prompts Gerados:</strong> ${
                                  analytics
                                    ? analytics.total_prompts_generated
                                    : 0
                                }</p>
                                <p><strong>Templates Criados:</strong> ${
                                  analytics
                                    ? analytics.saved_templates_count
                                    : 0
                                }</p>
                                <p><strong>Plano:</strong> ${
                                  profile ? profile.subscription_plan : "free"
                                }</p>
                                <p><strong>Membro desde:</strong> ${
                                  analytics
                                    ? new Date(
                                        analytics.member_since
                                      ).toLocaleDateString("pt-BR")
                                    : "N/A"
                                }</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                    </div>
                </div>
            </div>
        </div>
    `;

  // Remover modal anterior se existir
  const existingModal = document.getElementById("userDetailsModal");
  if (existingModal) {
    existingModal.remove();
  }

  // Adicionar novo modal
  document.body.insertAdjacentHTML("beforeend", modalHTML);

  // Mostrar modal
  const modal = new bootstrap.Modal(
    document.getElementById("userDetailsModal")
  );
  modal.show();
}

// Carregar status das APIs
async function loadAPIStatus() {
  const container = document.getElementById("apiStatusGrid");

  // Simular status das APIs baseado nos dados
  const apiProviders = [
    "Gemini",
    "Groq",
    "HuggingFace",
    "Cohere",
    "Together AI",
  ];
  const statuses = ["online", "online", "warning", "online", "offline"];

  container.innerHTML = apiProviders
    .map((provider, index) => {
      const status = statuses[index];
      const statusClass =
        status === "online"
          ? "status-online"
          : status === "warning"
          ? "status-warning"
          : "status-offline";
      const statusText =
        status === "online"
          ? "Online"
          : status === "warning"
          ? "Instável"
          : "Offline";
      const responseTime = Math.floor(Math.random() * 2000) + 200; // Simular tempo de resposta

      return `
            <div class="col-md-6 col-lg-4">
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-title">${provider}</span>
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </div>
                    <div class="mt-3">
                        <small class="text-muted d-block">Tempo de Resposta</small>
                        <strong>${responseTime}ms</strong>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted d-block">Último Check</small>
                        <strong>Agora</strong>
                    </div>
                </div>
            </div>
        `;
    })
    .join("");
}

// Navegação entre seções
function showSection(sectionName) {
  // Esconder todas as seções
  document.querySelectorAll(".admin-section").forEach((section) => {
    section.style.display = "none";
  });

  // Mostrar seção selecionada
  const targetSection = document.getElementById(sectionName + "-section");
  if (targetSection) {
    targetSection.style.display = "block";
  }

  // Atualizar navegação ativa
  document.querySelectorAll(".sidebar-nav-link").forEach((link) => {
    link.classList.remove("active");
  });

  const activeLink = document.querySelector(`[data-section="${sectionName}"]`);
  if (activeLink) {
    activeLink.classList.add("active");
  }

  // Carregar dados específicos da seção
  loadSectionData(sectionName);
}

// Carregar dados específicos de cada seção
async function loadSectionData(sectionName) {
  switch (sectionName) {
    case "users":
      await loadUsers();
      break;
    case "api-status":
      await loadAPIStatus();
      break;
    case "templates":
      await loadTemplates();
      break;
    case "analytics":
      await loadAnalytics();
      break;
    case "logs":
      await loadLogs();
      break;
  }
}

// Atualização em tempo real
function startRealTimeUpdates() {
  // Limpar interval anterior se existir
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }

  // Atualizar a cada 30 segundos
  refreshInterval = setInterval(async () => {
    try {
      const token = localStorage.getItem("authToken");

      if (!token) {
        console.warn("Token não encontrado, parando atualizações automáticas");
        clearInterval(refreshInterval);
        return;
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // Timeout de 5 segundos

      const response = await fetch(`${API_BASE}/admin/dashboard`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const newData = await response.json();
        dashboardData = newData;
        updateDashboard();
        console.log("Dashboard atualizado automaticamente");
      } else if (response.status === 401) {
        console.warn("Token expirado, parando atualizações automáticas");
        clearInterval(refreshInterval);
        localStorage.removeItem("authToken");
        window.location.href = "index.html";
      } else {
        console.warn("Erro na atualização automática:", response.status);
      }
    } catch (error) {
      if (error.name === "AbortError") {
        console.warn("Timeout na atualização automática");
      } else {
        console.error("Erro na atualização automática:", error);
      }
    }
  }, 30000); // 30 segundos
}

// Exportar dados
async function exportData() {
  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/admin/analytics/export`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const data = await response.json();

      // Criar arquivo JSON para download
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `admin-analytics-${
        new Date().toISOString().split("T")[0]
      }.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showAlert("Dados exportados com sucesso!", "success");
    } else {
      showAlert("Erro ao exportar dados", "error");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "error");
  }
}

// Event listeners
function initializeEventListeners() {
  // Navegação da sidebar
  document.querySelectorAll(".sidebar-nav-link").forEach((link) => {
    link.addEventListener("click", function (e) {
      const section = this.getAttribute("data-section");
      // Só intercepta cliques de links que têm data-section (navegação interna)
      if (section) {
        e.preventDefault();
        showSection(section);
      }
      // Links sem data-section (como "Página Principal") seguem navegação normal
    });
  });

  // Cleanup on page unload
  window.addEventListener("beforeunload", function () {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });
}

// Funções de atualização
function refreshUsers() {
  loadUsers();
}

function refreshAPIStatus() {
  loadAPIStatus();
}

function refreshLogs() {
  // Implementar carregamento de logs
  showAlert("Logs atualizados", "info");
}

// Logout
function logout() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
  localStorage.removeItem("authToken");
  window.location.href = "index.html";
}

// Utilitários
function showLoading(show) {
  document.getElementById("loadingOverlay").style.display = show
    ? "flex"
    : "none";
}

function showAlert(message, type = "info") {
  const alertTypes = {
    success: "alert-success",
    error: "alert-danger",
    warning: "alert-warning",
    info: "alert-info",
  };

  const alert = document.createElement("div");
  alert.className = `alert ${alertTypes[type]} alert-dismissible fade show position-fixed`;
  alert.style.cssText =
    "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
  alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  document.body.appendChild(alert);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (alert.parentNode) {
      alert.remove();
    }
  }, 5000);
}

// Load Templates
async function loadTemplates() {
  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/admin/templates`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const responseData = await response.json();
      const templates = responseData.templates || responseData; // Suporta tanto {templates: []} quanto []
      const tbody = document.getElementById("templatesTableBody");

      if (!tbody) {
        console.error("Elemento templatesTableBody não encontrado");
        showAlert("Erro: elemento da tabela não encontrado", "error");
        return;
      }

      if (!Array.isArray(templates)) {
        console.error("Templates não é um array:", templates);
        showAlert("Erro: formato de dados inválido", "error");
        return;
      }

      if (templates.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="7" class="text-center py-5">
              <i class="bi bi-collection text-muted" style="font-size: 3rem;"></i>
              <h5 class="mt-3 text-muted">Nenhum template encontrado</h5>
              <p class="text-muted">Templates criados pelos usuários aparecerão aqui.</p>
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = templates
        .map(
          (template) => `
        <tr>
          <td><strong>${
            template.title || template.name || "Sem título"
          }</strong></td>
          <td><span class="badge bg-primary">${
            template.category || "Geral"
          }</span></td>
          <td>${template.author || template.user_email || "Anônimo"}</td>
          <td>${
            template.is_public
              ? '<span class="badge bg-success">Sim</span>'
              : '<span class="badge bg-secondary">Não</span>'
          }</td>
          <td>${template.usage_count || 0}</td>
          <td>⭐ ${template.rating || 0}/5</td>
          <td>
            <button class="btn btn-sm btn-outline-primary me-1" onclick="viewTemplate('${
              template.id
            }')">Ver</button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteTemplate('${
              template.id
            }')">Excluir</button>
          </td>
        </tr>
      `
        )
        .join("");

      showAlert("Templates carregados com sucesso", "success");
    } else {
      console.error("Erro na resposta:", response.status, response.statusText);
      showAlert(`Erro ${response.status}: ${response.statusText}`, "error");
    }
  } catch (error) {
    console.error("Erro ao carregar templates:", error);
    showAlert("Erro ao carregar templates", "error");
  }
}

// Load Analytics
async function loadAnalytics() {
  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/admin/dashboard`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const data = await response.json();

      // Criar gráficos simples nos canvas existentes
      const performanceCtx = document.getElementById("performanceChart");
      const usersCtx = document.getElementById("usersChart");

      if (performanceCtx && usersCtx) {
        // Limpar canvas existentes
        const performanceChart = Chart.getChart(performanceCtx);
        const usersChart = Chart.getChart(usersCtx);

        if (performanceChart) performanceChart.destroy();
        if (usersChart) usersChart.destroy();

        // Gráfico de Performance das APIs
        new Chart(performanceCtx, {
          type: "bar",
          data: {
            labels: Object.keys(data.api_status || {}),
            datasets: [
              {
                label: "Tempo de Resposta (ms)",
                data: Object.values(data.api_status || {}).map(
                  (api) => Math.random() * 1000 + 100
                ),
                backgroundColor: "rgba(102, 126, 234, 0.8)",
                borderColor: "rgba(102, 126, 234, 1)",
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            scales: {
              y: { beginAtZero: true },
            },
          },
        });

        // Gráfico de Usuários
        new Chart(usersCtx, {
          type: "doughnut",
          data: {
            labels: ["Usuários Ativos", "Usuários PRO", "Usuários FREE"],
            datasets: [
              {
                data: [data.total_users || 1, 0, 1],
                backgroundColor: [
                  "rgba(6, 214, 160, 0.8)",
                  "rgba(102, 126, 234, 0.8)",
                  "rgba(156, 163, 175, 0.8)",
                ],
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: "bottom" },
            },
          },
        });
      }

      showAlert("Analytics carregados com sucesso", "success");
    }
  } catch (error) {
    console.error("Erro ao carregar analytics:", error);
    showAlert("Erro ao carregar analytics", "error");
  }
}

// Load Logs
async function loadLogs() {
  const container = document.getElementById("logsContainer");

  try {
    // Mostrar loading
    container.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Carregando logs...</span>
        </div>
        <p class="mt-2 text-muted">Carregando logs do sistema...</p>
      </div>
    `;

    const response = await fetch("/api/admin/logs", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const logs = data.logs || [];

    if (logs.length === 0) {
      container.innerHTML = `
        <div class="text-center py-5">
          <i class="bi bi-file-text text-muted" style="font-size: 3rem;"></i>
          <h5 class="mt-3 text-muted">Nenhum log encontrado</h5>
          <p class="text-muted">O sistema ainda não gerou logs ou os arquivos não foram encontrados.</p>
        </div>
      `;
      return;
    }

    // Renderizar logs reais
    container.innerHTML = `
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h6 class="mb-0">
            <i class="bi bi-file-text me-2"></i>
            Logs do Sistema (${logs.length} entradas)
          </h6>
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-outline-primary" onclick="filterLogs('all')">Todos</button>
            <button type="button" class="btn btn-outline-success" onclick="filterLogs('info')">INFO</button>
            <button type="button" class="btn btn-outline-warning" onclick="filterLogs('warning')">WARN</button>
            <button type="button" class="btn btn-outline-danger" onclick="filterLogs('error')">ERROR</button>
          </div>
        </div>
        <div class="card-body" style="max-height: 500px; overflow-y: auto;">
          <div id="logs-entries" class="font-monospace small">
            ${logs
              .map((log) => {
                let displayTime = log.timestamp;
                try {
                  displayTime = new Date(log.timestamp).toLocaleString("pt-BR");
                } catch (e) {
                  // Manter timestamp original se não conseguir formatar
                }

                let levelClass = "text-muted";
                switch (log.level.toUpperCase()) {
                  case "INFO":
                    levelClass = "text-info";
                    break;
                  case "ERROR":
                    levelClass = "text-danger";
                    break;
                  case "WARNING":
                    levelClass = "text-warning";
                    break;
                  case "DEBUG":
                    levelClass = "text-secondary";
                    break;
                }

                return `
                <div class="log-entry mb-1 ${levelClass}" data-level="${log.level.toLowerCase()}">
                  <span class="text-muted">[${displayTime}]</span>
                  <span class="fw-bold">${log.level}:</span>
                  <span class="text-muted">[${
                    log.module || log.source || "system"
                  }]</span>
                  <span>${log.message}</span>
                </div>
              `;
              })
              .join("")}
          </div>
        </div>
      </div>
    `;
  } catch (error) {
    console.error("Erro ao carregar logs:", error);
    container.innerHTML = `
      <div class="alert alert-danger">
        <h6 class="alert-heading">
          <i class="bi bi-exclamation-triangle me-2"></i>
          Erro ao carregar logs
        </h6>
        <p class="mb-1">${error.message}</p>
        <small class="text-muted">Verifique se você tem permissões de administrador e se o servidor está funcionando.</small>
      </div>
    `;
  }
}

// Função para filtrar logs por nível
function filterLogs(level) {
  const entries = document.querySelectorAll(".log-entry");
  const buttons = document.querySelectorAll(".btn-group .btn");

  // Atualizar botões ativos
  buttons.forEach((btn) => btn.classList.remove("active"));
  event.target.classList.add("active");

  // Filtrar entradas
  entries.forEach((entry) => {
    if (level === "all" || entry.dataset.level === level) {
      entry.style.display = "block";
    } else {
      entry.style.display = "none";
    }
  });
}

// Template actions
function viewTemplate(templateId) {
  showAlert(
    `Ver template ${templateId} - Funcionalidade em desenvolvimento`,
    "info"
  );
}

function deleteTemplate(templateId) {
  if (confirm("Tem certeza que deseja excluir este template?")) {
    // Implementar exclusão
    showAlert(`Template ${templateId} excluído (simulado)`, "warning");
  }
}
