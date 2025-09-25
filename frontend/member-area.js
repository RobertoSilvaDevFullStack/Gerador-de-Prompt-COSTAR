/**
 * JavaScript para Área de Membros
 */

// Configurações
const API_BASE = "/api";
let currentUser = null;
let currentProfile = null;

// Inicialização
document.addEventListener("DOMContentLoaded", function () {
  checkAuthentication();
  initializeEventListeners();
});

// Verificar autenticação
async function checkAuthentication() {
  const token = localStorage.getItem("authToken");

  if (!token) {
    window.location.href = "index.html";
    return;
  }

  try {
    showLoading(true);

    // Carregar perfil do usuário
    const response = await fetch(`${API_BASE}/members/profile`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      currentProfile = data.profile;
      updateUI();
    } else if (response.status === 401) {
      localStorage.removeItem("authToken");
      window.location.href = "index.html";
    } else {
      showAlert("Erro ao carregar perfil", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  } finally {
    showLoading(false);
  }
}

// Atualizar interface com dados do usuário
function updateUI() {
  if (!currentProfile) return;

  // Atualizar badge de assinatura
  updateSubscriptionBadge();

  // Carregar dados das abas
  loadDashboardData();
  loadUserTemplates();
  loadPublicTemplates();
  loadProfileForm();
}

// Atualizar badge de assinatura
function updateSubscriptionBadge() {
  const badge = document.getElementById("subscriptionBadge");
  const plan = currentProfile.subscription_plan;

  badge.textContent = plan.charAt(0).toUpperCase() + plan.slice(1);
  badge.className = `subscription-badge subscription-${plan}`;
}

// Carregar dados do dashboard
async function loadDashboardData() {
  try {
    const token = localStorage.getItem("authToken");

    // Carregar analytics
    const analyticsResponse = await fetch(`${API_BASE}/members/analytics`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (analyticsResponse.ok) {
      const analytics = await analyticsResponse.json();
      updateDashboardStats(analytics);
    }

    // Carregar quotas
    const quotaResponse = await fetch(`${API_BASE}/members/quota`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (quotaResponse.ok) {
      const quotas = await quotaResponse.json();
      updateQuotaDisplay(quotas);
    }
  } catch (error) {
    console.error("Erro ao carregar dashboard:", error);
  }
}

// Atualizar estatísticas do dashboard
function updateDashboardStats(analytics) {
  document.getElementById("totalPrompts").textContent =
    analytics.total_prompts_generated || 0;
  document.getElementById("monthlyPrompts").textContent =
    analytics.prompts_this_month || 0;
  document.getElementById("savedTemplates").textContent =
    analytics.saved_templates_count || 0;

  // Formatar data de membro desde
  if (analytics.member_since) {
    const memberDate = new Date(analytics.member_since);
    const months = Math.floor(
      (Date.now() - memberDate.getTime()) / (1000 * 60 * 60 * 24 * 30)
    );
    document.getElementById("memberSince").textContent = `${months}m`;
  }
}

// Atualizar display de quotas
function updateQuotaDisplay(quotas) {
  // Quota de prompts
  const promptsQuota = quotas.prompts;
  if (promptsQuota.limit !== -1) {
    document.getElementById("promptsUsed").textContent = promptsQuota.used;
    document.getElementById("promptsLimit").textContent = promptsQuota.limit;

    const percentage = promptsQuota.percentage;
    const progressBar = document.getElementById("promptsProgress");
    progressBar.style.width = `${percentage}%`;

    // Alterar cor baseada na porcentagem
    progressBar.className =
      "quota-progress " +
      (percentage >= 90 ? "danger" : percentage >= 70 ? "warning" : "good");
  } else {
    document.getElementById("promptsUsed").textContent = promptsQuota.used;
    document.getElementById("promptsLimit").textContent = "∞";
    document.getElementById("promptsProgress").style.width = "100%";
  }

  // Quota de templates
  const templatesQuota = quotas.templates;
  if (templatesQuota.limit !== -1) {
    document.getElementById("templatesUsed").textContent = templatesQuota.used;
    document.getElementById("templatesLimit").textContent =
      templatesQuota.limit;

    const percentage = templatesQuota.percentage;
    const progressBar = document.getElementById("templatesProgress");
    progressBar.style.width = `${percentage}%`;

    progressBar.className =
      "quota-progress " +
      (percentage >= 90 ? "danger" : percentage >= 70 ? "warning" : "good");
  } else {
    document.getElementById("templatesUsed").textContent = templatesQuota.used;
    document.getElementById("templatesLimit").textContent = "∞";
    document.getElementById("templatesProgress").style.width = "100%";
  }
}

// Carregar templates do usuário
async function loadUserTemplates() {
  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/members/templates`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const data = await response.json();
      displayUserTemplates(data.templates);
    }
  } catch (error) {
    console.error("Erro ao carregar templates:", error);
  }
}

// Exibir templates do usuário
function displayUserTemplates(templates) {
  const container = document.getElementById("userTemplates");

  if (templates.length === 0) {
    container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="bi bi-collection display-1 text-muted"></i>
                    <h5 class="mt-3 text-muted">Nenhum template criado</h5>
                    <p class="text-muted">Crie seu primeiro template personalizado!</p>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createTemplateModal">
                        <i class="bi bi-plus-circle me-2"></i>Criar Template
                    </button>
                </div>
            </div>
        `;
    return;
  }

  container.innerHTML = templates
    .map(
      (template) => `
        <div class="col-md-6 col-lg-4">
            <div class="template-card">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0">${template.name}</h6>
                    <span class="badge bg-secondary">${template.category}</span>
                </div>
                <p class="text-muted small mb-2">${template.description}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <small class="text-muted">
                            <i class="bi bi-eye me-1"></i>${
                              template.usage_count
                            } usos
                        </small>
                        ${
                          template.is_public
                            ? '<span class="badge bg-success ms-2">Público</span>'
                            : ""
                        }
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="useTemplate('${
                          template.id
                        }')">
                            <i class="bi bi-play"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="editTemplate('${
                          template.id
                        }')">
                            <i class="bi bi-pencil"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `
    )
    .join("");
}

// Carregar templates públicos
async function loadPublicTemplates(category = "", search = "") {
  try {
    const token = localStorage.getItem("authToken");
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (search) params.append("search", search);

    const response = await fetch(
      `${API_BASE}/members/templates/public?${params}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    if (response.ok) {
      const data = await response.json();
      displayPublicTemplates(data.templates);
    }
  } catch (error) {
    console.error("Erro ao carregar templates públicos:", error);
  }
}

// Exibir templates públicos
function displayPublicTemplates(templates) {
  const container = document.getElementById("publicTemplates");

  if (templates.length === 0) {
    container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="bi bi-search display-1 text-muted"></i>
                    <h5 class="mt-3 text-muted">Nenhum template encontrado</h5>
                    <p class="text-muted">Tente ajustar os filtros de busca.</p>
                </div>
            </div>
        `;
    return;
  }

  container.innerHTML = templates
    .map(
      (template) => `
        <div class="col-md-6 col-lg-4">
            <div class="template-card">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0">${template.name}</h6>
                    <span class="badge bg-primary">${template.category}</span>
                </div>
                <p class="text-muted small mb-2">${template.description}</p>
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div class="template-rating">
                        ${generateStarRating(template.rating)}
                        <small class="text-muted ms-1">(${
                          template.votes
                        })</small>
                    </div>
                    <small class="text-muted">
                        <i class="bi bi-eye me-1"></i>${
                          template.usage_count
                        } usos
                    </small>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-primary flex-fill" onclick="usePublicTemplate('${
                      template.id
                    }')">
                        <i class="bi bi-play me-1"></i>Usar
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="rateTemplate('${
                      template.id
                    }')">
                        <i class="bi bi-star"></i>
                    </button>
                </div>
            </div>
        </div>
    `
    )
    .join("");
}

// Gerar estrelas de rating
function generateStarRating(rating) {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  let stars = "";

  for (let i = 0; i < fullStars; i++) {
    stars += '<i class="bi bi-star-fill"></i>';
  }

  if (hasHalfStar) {
    stars += '<i class="bi bi-star-half"></i>';
  }

  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
  for (let i = 0; i < emptyStars; i++) {
    stars += '<i class="bi bi-star"></i>';
  }

  return stars;
}

// Carregar formulário de perfil
function loadProfileForm() {
  if (!currentProfile) return;

  document.getElementById("username").value = currentProfile.username || "";
  document.getElementById("email").value = currentProfile.email || "";

  const preferences = currentProfile.preferences || {};
  document.getElementById("defaultStyle").value =
    preferences.default_style || "professional";
  document.getElementById("defaultTone").value =
    preferences.default_tone || "neutral";
  document.getElementById("autoSavePrompts").checked =
    preferences.auto_save_prompts !== false;
  document.getElementById("emailNotifications").checked =
    preferences.email_notifications !== false;
}

// Criar template
async function createTemplate() {
  const form = document.getElementById("createTemplateForm");
  const formData = new FormData(form);

  const templateData = {
    name: document.getElementById("templateName").value,
    description: document.getElementById("templateDescription").value,
    category: document.getElementById("templateCategory").value,
    template_content: {
      context: document.getElementById("templateContext").value,
      task: document.getElementById("templateTask").value,
      style: document.getElementById("templateStyle").value,
      tone: document.getElementById("templateTone").value,
      audience: document.getElementById("templateAudience").value,
      response: document.getElementById("templateResponse").value,
    },
    is_public: document.getElementById("templatePublic").checked,
    tags: document
      .getElementById("templateTags")
      .value.split(",")
      .map((tag) => tag.trim())
      .filter((tag) => tag),
  };

  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/members/templates`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(templateData),
    });

    if (response.ok) {
      showAlert("Template criado com sucesso!", "success");
      bootstrap.Modal.getInstance(
        document.getElementById("createTemplateModal")
      ).hide();
      form.reset();
      loadUserTemplates();
      loadDashboardData(); // Atualizar quotas
    } else {
      const error = await response.json();
      showAlert(error.detail || "Erro ao criar template", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  }
}

// Usar template
async function useTemplate(templateId) {
  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(
      `${API_BASE}/members/templates/${templateId}/use`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    if (response.ok) {
      const data = await response.json();
      // Redirecionar para página principal com template carregado
      localStorage.setItem("selectedTemplate", JSON.stringify(data.template));
      window.location.href = "index.html";
    } else {
      showAlert("Erro ao usar template", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  }
}

// Usar template público
async function usePublicTemplate(templateId) {
  await useTemplate(templateId);
}

// Avaliar template
async function rateTemplate(templateId) {
  const rating = prompt("Avalie este template (1-5 estrelas):");
  if (!rating || rating < 1 || rating > 5) return;

  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(
      `${API_BASE}/members/templates/${templateId}/rate`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ rating: parseFloat(rating) }),
      }
    );

    if (response.ok) {
      showAlert("Avaliação registrada!", "success");
      loadPublicTemplates(); // Recarregar templates
    } else {
      showAlert("Erro ao avaliar template", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  }
}

// Fazer upgrade de assinatura
async function upgradeSubscription(newPlan) {
  if (!confirm(`Deseja fazer upgrade para o plano ${newPlan.toUpperCase()}?`))
    return;

  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/members/subscription/upgrade`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ new_plan: newPlan }),
    });

    if (response.ok) {
      showAlert("Assinatura atualizada com sucesso!", "success");
      // Recarregar página para atualizar interface
      setTimeout(() => window.location.reload(), 2000);
    } else {
      const error = await response.json();
      showAlert(error.detail || "Erro ao fazer upgrade", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  }
}

// Salvar perfil
async function saveProfile(event) {
  event.preventDefault();

  const profileData = {
    username: document.getElementById("username").value,
    preferences: {
      default_style: document.getElementById("defaultStyle").value,
      default_tone: document.getElementById("defaultTone").value,
      auto_save_prompts: document.getElementById("autoSavePrompts").checked,
      email_notifications:
        document.getElementById("emailNotifications").checked,
    },
  };

  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/members/profile`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(profileData),
    });

    if (response.ok) {
      showAlert("Perfil atualizado com sucesso!", "success");
      // Atualizar perfil atual
      currentProfile.username = profileData.username;
      currentProfile.preferences = {
        ...currentProfile.preferences,
        ...profileData.preferences,
      };
    } else {
      showAlert("Erro ao atualizar perfil", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  }
}

// Logout
function logout() {
  localStorage.removeItem("authToken");
  window.location.href = "index.html";
}

// Event listeners
function initializeEventListeners() {
  // Formulário de perfil
  document
    .getElementById("profileForm")
    .addEventListener("submit", saveProfile);

  // Filtros de templates públicos
  document
    .getElementById("categoryFilter")
    .addEventListener("change", function () {
      const category = this.value;
      const search = document.getElementById("searchFilter").value;
      loadPublicTemplates(category, search);
    });

  document
    .getElementById("searchFilter")
    .addEventListener("input", function () {
      const search = this.value;
      const category = document.getElementById("categoryFilter").value;
      // Debounce search
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        loadPublicTemplates(category, search);
      }, 500);
    });

  // Tabs - recarregar dados quando necessário
  document.querySelectorAll('button[data-bs-toggle="pill"]').forEach((tab) => {
    tab.addEventListener("shown.bs.tab", function (event) {
      const target = event.target.getAttribute("data-bs-target");

      if (target === "#explore") {
        loadPublicTemplates();
      } else if (target === "#templates") {
        loadUserTemplates();
      }
    });
  });
}

// Utilitários
function showLoading(show) {
  document.getElementById("loadingOverlay").style.display = show
    ? "block"
    : "none";
}

function showAlert(message, type = "info") {
  const alert = document.createElement("div");
  alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
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
