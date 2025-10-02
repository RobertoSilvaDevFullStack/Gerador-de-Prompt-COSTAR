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
  loadSavedPrompts(); // Carregar prompts salvos também
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
  // Usar os nomes corretos dos campos da API
  document.getElementById("totalPrompts").textContent =
    analytics.prompts_generated_total || 0;
  document.getElementById("monthlyPrompts").textContent =
    analytics.prompts_generated_this_month || 0;
  document.getElementById("savedTemplates").textContent =
    analytics.saved_prompts_count || 0; // Corrigido para prompts salvos

  // Mostrar templates também se disponível
  const templatesElement = document.getElementById("templatesCount");
  if (templatesElement) {
    templatesElement.textContent = analytics.templates_count || 0;
  }

  // Formatar data de membro desde
  if (analytics.member_since) {
    const memberDate = new Date(analytics.member_since);
    const months = Math.floor(
      (Date.now() - memberDate.getTime()) / (1000 * 60 * 60 * 24 * 30)
    );
    document.getElementById("memberSince").textContent = `${months}m`;
  }

  // Mostrar taxa de sucesso se disponível
  const successRateElement = document.getElementById("successRate");
  if (successRateElement && analytics.success_rate !== undefined) {
    successRateElement.textContent = `${analytics.success_rate.toFixed(1)}%`;
  }
}

// Atualizar display de quotas
function updateQuotaDisplay(quotas) {
  // Nova estrutura de quota mensal
  if (quotas.used !== undefined && quotas.limit !== undefined) {
    document.getElementById("promptsUsed").textContent = quotas.used;

    if (quotas.limit === "unlimited") {
      document.getElementById("promptsLimit").textContent = "∞";
      document.getElementById("promptsProgress").style.width = "100%";
      document.getElementById("promptsProgress").className =
        "quota-progress good";
    } else {
      document.getElementById("promptsLimit").textContent = quotas.limit;

      const percentage =
        quotas.limit > 0 ? (quotas.used / quotas.limit) * 100 : 0;
      const progressBar = document.getElementById("promptsProgress");
      progressBar.style.width = `${Math.min(percentage, 100)}%`;

      // Alterar cor baseada na porcentagem
      progressBar.className =
        "quota-progress " +
        (percentage >= 90 ? "danger" : percentage >= 70 ? "warning" : "good");
    }

    // Mostrar aviso se quota excedida
    if (!quotas.allowed && quotas.reason) {
      showAlert(`Atenção: ${quotas.reason}`, "warning");
    }

    return;
  }

  // Fallback para estrutura antiga se existir
  const promptsQuota = quotas.prompts;
  if (promptsQuota && promptsQuota.limit !== undefined) {
    if (promptsQuota.limit !== -1) {
      document.getElementById("promptsUsed").textContent = promptsQuota.used;
      document.getElementById("promptsLimit").textContent = promptsQuota.limit;

      const percentage = promptsQuota.percentage || 0;
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
  }

  // Quota de templates (se existir)
  const templatesQuota = quotas.templates;
  if (templatesQuota && templatesQuota.limit !== undefined) {
    if (templatesQuota.limit !== -1) {
      document.getElementById("templatesUsed").textContent =
        templatesQuota.used;
      document.getElementById("templatesLimit").textContent =
        templatesQuota.limit;

      const percentage = templatesQuota.percentage;
      const progressBar = document.getElementById("templatesProgress");
      progressBar.style.width = `${percentage}%`;

      progressBar.className =
        "quota-progress " +
        (percentage >= 90 ? "danger" : percentage >= 70 ? "warning" : "good");
    } else {
      document.getElementById("templatesUsed").textContent =
        templatesQuota.used;
      document.getElementById("templatesLimit").textContent = "∞";
      document.getElementById("templatesProgress").style.width = "100%";
    }
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
    console.log("📡 loadPublicTemplates chamado com:", { category, search });
    const token = localStorage.getItem("authToken");
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (search) params.append("search", search);

    const url = `${API_BASE}/members/templates/public?${params}`;
    console.log("📡 URL da requisição:", url);

    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const data = await response.json();
      console.log("📦 Dados recebidos:", data);
      // O endpoint retorna diretamente a lista de templates
      displayPublicTemplates(Array.isArray(data) ? data : data.templates || []);
    } else {
      console.error("Erro ao carregar templates:", response.status);
      displayPublicTemplates([]);
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
      console.log("🔍 Filtro categoria alterado:", category, "busca:", search);
      loadPublicTemplates(category, search);
    });

  document
    .getElementById("searchFilter")
    .addEventListener("input", function () {
      const search = this.value;
      const category = document.getElementById("categoryFilter").value;
      console.log("🔍 Filtro busca alterado:", search, "categoria:", category);
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

  // Inicializar event listeners das abas de prompts salvos
  initializeTabEventListeners();
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

// ===== FUNÇÕES DE SECURITY (ALTERAÇÃO DE SENHA) =====

// Toggle visibility de senha
function togglePasswordVisibility(fieldId) {
  const field = document.getElementById(fieldId);
  const icon = document.getElementById(fieldId + "Icon");

  if (field.type === "password") {
    field.type = "text";
    icon.className = "bi bi-eye-slash";
  } else {
    field.type = "password";
    icon.className = "bi bi-eye";
  }
}

// Verificar força da senha
function checkPasswordStrength(password) {
  let strength = 0;
  let feedback = [];

  if (password.length >= 8) strength += 1;
  else feedback.push("Pelo menos 8 caracteres");

  if (/[a-z]/.test(password)) strength += 1;
  else feedback.push("Letras minúsculas");

  if (/[A-Z]/.test(password)) strength += 1;
  else feedback.push("Letras maiúsculas");

  if (/\d/.test(password)) strength += 1;
  else feedback.push("Números");

  if (/[^A-Za-z0-9]/.test(password)) strength += 1;
  else feedback.push("Símbolos especiais");

  return { strength, feedback };
}

// Atualizar indicador de força da senha
function updatePasswordStrength() {
  const password = document.getElementById("newPassword").value;
  const strengthBar = document.getElementById("passwordStrength");
  const strengthText = document.getElementById("passwordStrengthText");

  if (!password) {
    strengthBar.style.width = "0%";
    strengthBar.className = "progress-bar";
    strengthText.textContent = "Digite uma nova senha para verificar a força";
    return;
  }

  const { strength, feedback } = checkPasswordStrength(password);
  const percentage = (strength / 5) * 100;

  strengthBar.style.width = percentage + "%";

  if (strength <= 2) {
    strengthBar.className = "progress-bar bg-danger";
    strengthText.textContent = "Fraca - Adicione: " + feedback.join(", ");
  } else if (strength <= 3) {
    strengthBar.className = "progress-bar bg-warning";
    strengthText.textContent = "Média - Melhore: " + feedback.join(", ");
  } else if (strength <= 4) {
    strengthBar.className = "progress-bar bg-info";
    strengthText.textContent = "Boa - Quase perfeita!";
  } else {
    strengthBar.className = "progress-bar bg-success";
    strengthText.textContent = "Excelente - Senha muito segura!";
  }
}

// Event listener para alteração de senha
document.addEventListener("DOMContentLoaded", function () {
  const newPasswordField = document.getElementById("newPassword");
  if (newPasswordField) {
    newPasswordField.addEventListener("input", updatePasswordStrength);
  }

  // Form de alteração de senha
  const changePasswordForm = document.getElementById("changePasswordForm");
  if (changePasswordForm) {
    changePasswordForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      await handleChangePassword();
    });
  }
});

// Alterar senha
async function handleChangePassword() {
  const currentPassword = document.getElementById("currentPassword").value;
  const newPassword = document.getElementById("newPassword").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  if (newPassword !== confirmPassword) {
    showAlert("As senhas não coincidem", "danger");
    return;
  }

  const { strength } = checkPasswordStrength(newPassword);
  if (strength < 3) {
    showAlert("A senha deve ser mais forte", "warning");
    return;
  }

  try {
    showLoading(true);

    const response = await fetch(`${API_BASE}/members/change-password`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showAlert("Senha alterada com sucesso!", "success");
      document.getElementById("changePasswordForm").reset();
      updatePasswordStrength();
    } else {
      showAlert(data.message || "Erro ao alterar senha", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  } finally {
    showLoading(false);
  }
}

// Salvar configurações de segurança
async function saveSecuritySettings() {
  const twoFactorAuth = document.getElementById("twoFactorAuth").checked;
  const loginNotifications =
    document.getElementById("loginNotifications").checked;

  try {
    showLoading(true);

    const response = await fetch(`${API_BASE}/members/security-settings`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        two_factor_auth: twoFactorAuth,
        login_notifications: loginNotifications,
      }),
    });

    if (response.ok) {
      showAlert("Configurações de segurança salvas!", "success");
    } else {
      showAlert("Erro ao salvar configurações", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  } finally {
    showLoading(false);
  }
}

// ===== FUNÇÕES DE SUBSCRIPTION (ASSINATURA) =====

// Selecionar plano
function selectPlan(planType) {
  document.getElementById("selectedPlan").value = planType;

  // Atualizar resumo do pedido
  const planNames = {
    premium: "Premium",
    enterprise: "Enterprise",
  };

  const planPrices = {
    premium: 29.0,
    enterprise: 99.0,
  };

  const planPrice = planPrices[planType];
  const total = planPrice + 2.5; // Taxa de processamento

  document.getElementById("orderPlanName").textContent = planNames[planType];
  document.getElementById(
    "orderPlanPrice"
  ).textContent = `R$ ${planPrice.toFixed(2)}/mês`;
  document.getElementById("orderTotal").textContent = `R$ ${total.toFixed(2)}`;

  // Mostrar formulário de pagamento
  document.getElementById("paymentForm").style.display = "block";

  // Scroll para o formulário
  document.getElementById("paymentForm").scrollIntoView({ behavior: "smooth" });
}

// Preencher endereço por CEP
async function fillAddressByCEP() {
  const cep = document
    .getElementById("billingZipCode")
    .value.replace(/\D/g, "");

  if (cep.length !== 8) return;

  try {
    const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
    const data = await response.json();

    if (!data.erro) {
      document.getElementById("billingStreet").value = data.logradouro || "";
      document.getElementById("billingNeighborhood").value = data.bairro || "";
      document.getElementById("billingCity").value = data.localidade || "";
      document.getElementById("billingState").value = data.uf || "";
    }
  } catch (error) {
    console.error("Erro ao buscar CEP:", error);
  }
}

// Detectar bandeira do cartão
function detectCardBrand(number) {
  const brands = {
    visa: /^4[0-9]{12}(?:[0-9]{3})?$/,
    mastercard: /^5[1-5][0-9]{14}$/,
    amex: /^3[47][0-9]{13}$/,
    discover: /^6(?:011|5[0-9]{2})[0-9]{12}$/,
    elo: /^4011(78|79)|^43(1274|8935)|^45(1416|7393|763(1|2))|^50(4175|6699|67[0-6][0-9]|677[0-8]|9[0-8][0-9]{2}|99[0-8][0-9]|999[0-9])|^627780|^63(6297|6368|6369)|^65(0(0(3([1-3]|[5-9])|4([0-9])|5[0-1])|4(0[5-9]|[1-3][0-9]|8[5-9]|9[0-9])|5([0-2][0-9]|3[0-8]|4[1-9]|[5-8][0-9]|9[0-8])|7(0[0-9]|1[0-8]|2[0-7])|9(0[1-9]|[1-6][0-9]|7[0-8]))|16(5[2-9]|[6-7][0-9])|50(0[0-9]|1[0-9]|2[1-9]|[3-4][0-9]|5[0-8]))$/,
  };

  const cleanNumber = number.replace(/\D/g, "");

  for (const [brand, regex] of Object.entries(brands)) {
    if (regex.test(cleanNumber)) {
      return brand;
    }
  }

  return "unknown";
}

// Formatar campos de entrada
document.addEventListener("DOMContentLoaded", function () {
  // Formatação de telefone
  const phoneField = document.getElementById("billingPhone");
  if (phoneField) {
    phoneField.addEventListener("input", function (e) {
      let value = e.target.value.replace(/\D/g, "");
      value = value.replace(/(\d{2})(\d)/, "($1) $2");
      value = value.replace(/(\d{5})(\d{4})$/, "$1-$2");
      e.target.value = value;
    });
  }

  // Formatação de CPF/CNPJ
  const documentField = document.getElementById("billingDocument");
  if (documentField) {
    documentField.addEventListener("input", function (e) {
      let value = e.target.value.replace(/\D/g, "");
      if (value.length <= 11) {
        value = value.replace(/(\d{3})(\d)/, "$1.$2");
        value = value.replace(/(\d{3})(\d)/, "$1.$2");
        value = value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
      } else {
        value = value.replace(/(\d{2})(\d)/, "$1.$2");
        value = value.replace(/(\d{3})(\d)/, "$1.$2");
        value = value.replace(/(\d{3})(\d)/, "$1/$2");
        value = value.replace(/(\d{4})(\d{1,2})$/, "$1-$2");
      }
      e.target.value = value;
    });
  }

  // Formatação de CEP
  const cepField = document.getElementById("billingZipCode");
  if (cepField) {
    cepField.addEventListener("input", function (e) {
      let value = e.target.value.replace(/\D/g, "");
      value = value.replace(/(\d{5})(\d{3})$/, "$1-$2");
      e.target.value = value;
    });
  }

  // Formatação de número do cartão
  const cardNumberField = document.getElementById("cardNumber");
  if (cardNumberField) {
    cardNumberField.addEventListener("input", function (e) {
      let value = e.target.value.replace(/\D/g, "");
      value = value.replace(/(\d{4})(?=\d)/g, "$1 ");
      e.target.value = value;

      // Detectar bandeira
      const brand = detectCardBrand(value);
      const icon = document.getElementById("cardBrandIcon");

      const brandIcons = {
        visa: "bi-credit-card",
        mastercard: "bi-credit-card-fill",
        amex: "bi-credit-card-2-front",
        elo: "bi-credit-card-2-back",
        unknown: "bi-credit-card",
      };

      icon.className = brandIcons[brand] || "bi-credit-card";
    });
  }

  // Formatação de validade do cartão
  const cardExpiryField = document.getElementById("cardExpiry");
  if (cardExpiryField) {
    cardExpiryField.addEventListener("input", function (e) {
      let value = e.target.value.replace(/\D/g, "");
      value = value.replace(/(\d{2})(\d{2})$/, "$1/$2");
      e.target.value = value;
    });
  }

  // Form de assinatura
  const subscriptionForm = document.getElementById("subscriptionForm");
  if (subscriptionForm) {
    subscriptionForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      await handleSubscription();
    });
  }
});

// Processar assinatura
async function handleSubscription() {
  const formData = new FormData(document.getElementById("subscriptionForm"));
  const subscriptionData = Object.fromEntries(formData.entries());

  // Validações básicas
  if (!document.getElementById("agreeTerms").checked) {
    showAlert("Você deve aceitar os termos de uso", "warning");
    return;
  }

  if (!document.getElementById("agreeRecurring").checked) {
    showAlert("Você deve concordar com a cobrança recorrente", "warning");
    return;
  }

  try {
    showLoading(true);

    const response = await fetch(`${API_BASE}/members/subscribe`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        plan: document.getElementById("selectedPlan").value,
        billing_info: {
          name: document.getElementById("billingName").value,
          email: document.getElementById("billingEmail").value,
          phone: document.getElementById("billingPhone").value,
          document: document.getElementById("billingDocument").value,
          address: {
            zip_code: document.getElementById("billingZipCode").value,
            street: document.getElementById("billingStreet").value,
            number: document.getElementById("billingNumber").value,
            complement: document.getElementById("billingComplement").value,
            neighborhood: document.getElementById("billingNeighborhood").value,
            city: document.getElementById("billingCity").value,
            state: document.getElementById("billingState").value,
          },
        },
        payment_info: {
          card_number: document.getElementById("cardNumber").value,
          card_name: document.getElementById("cardName").value,
          card_expiry: document.getElementById("cardExpiry").value,
          card_cvv: document.getElementById("cardCVV").value,
          installments: document.getElementById("cardInstallments").value,
        },
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showSuccessModal(
        "Assinatura Ativada!",
        "Sua assinatura foi processada com sucesso. Bem-vindo ao plano premium!"
      );
      // Recarregar dados do usuário
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } else {
      showAlert(data.message || "Erro ao processar assinatura", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  } finally {
    showLoading(false);
  }
}

// Cancelar formulário de assinatura
function cancelSubscription() {
  document.getElementById("paymentForm").style.display = "none";
  document.getElementById("subscriptionForm").reset();
}

// Mostrar modal de cancelamento
function showCancelModal() {
  const modal = new bootstrap.Modal(
    document.getElementById("cancelSubscriptionModal")
  );
  modal.show();
}

// Confirmar cancelamento de assinatura
async function confirmCancelSubscription() {
  const reason = document.getElementById("cancelReason").value;
  const feedback = document.getElementById("cancelFeedback").value;

  try {
    showLoading(true);

    const response = await fetch(`${API_BASE}/members/cancel-subscription`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        reason,
        feedback,
      }),
    });

    if (response.ok) {
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("cancelSubscriptionModal")
      );
      modal.hide();

      showSuccessModal(
        "Assinatura Cancelada",
        "Sua assinatura foi cancelada e será efetiva no final do período atual."
      );

      // Recarregar dados
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } else {
      showAlert("Erro ao cancelar assinatura", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  } finally {
    showLoading(false);
  }
}

// Atualizar método de pagamento
function updatePaymentMethod() {
  showAlert("Funcionalidade em desenvolvimento", "info");
}

// Pausar assinatura
function pauseSubscription() {
  showAlert("Funcionalidade em desenvolvimento", "info");
}

// Mostrar modal de sucesso personalizado
function showSuccessModal(title, message) {
  document.getElementById("successTitle").textContent = title;
  document.getElementById("successMessage").textContent = message;

  const modal = new bootstrap.Modal(document.getElementById("successModal"));
  modal.show();
}

// ============= NOVAS FUNÇÕES - PROMPTS SALVOS E QUOTA =============

// Carregar prompts salvos do usuário
async function loadSavedPrompts() {
  console.log("🔄 [MEMBER] Carregando prompts salvos...");

  try {
    const token = localStorage.getItem("authToken");
    if (!token) {
      console.error("❌ [MEMBER] Token não encontrado");
      return;
    }

    console.log("📡 [MEMBER] Fazendo requisição para /members/saved-prompts");
    const response = await fetch(`${API_BASE}/members/saved-prompts`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    console.log(`📊 [MEMBER] Status da resposta: ${response.status}`);

    if (response.ok) {
      const data = await response.json();
      console.log("✅ [MEMBER] Dados recebidos:", data);
      console.log(
        `📋 [MEMBER] Total prompts: ${data.total}, Array length: ${data.prompts?.length}`
      );

      displaySavedPrompts(data.prompts);

      // Atualizar contador no dashboard
      const savedPromptsCount = document.getElementById("savedTemplates");
      if (savedPromptsCount) {
        savedPromptsCount.textContent = data.total;
        console.log(`📊 [MEMBER] Contador atualizado: ${data.total}`);
      } else {
        console.warn("⚠️ [MEMBER] Elemento savedTemplates não encontrado");
      }
    } else {
      const errorText = await response.text();
      console.error(
        `❌ [MEMBER] Erro na requisição: ${response.status}`,
        errorText
      );
    }
  } catch (error) {
    console.error("❌ [MEMBER] Erro ao carregar prompts salvos:", error);
  }
}

// Exibir prompts salvos na interface
function displaySavedPrompts(prompts) {
  console.log("🎨 [MEMBER] Exibindo prompts salvos:", prompts);

  const container = document.getElementById("savedPromptsContainer");
  if (!container) {
    console.error(
      "❌ [MEMBER] Container 'savedPromptsContainer' não encontrado"
    );
    return;
  }

  if (!prompts || prompts.length === 0) {
    console.log(
      "📭 [MEMBER] Nenhum prompt encontrado, exibindo mensagem vazia"
    );
    container.innerHTML = `
      <div class="text-center text-muted py-4">
        <i class="fas fa-save fa-3x mb-3"></i>
        <p>Nenhum prompt salvo ainda.</p>
        <p>Gere prompts e salve seus favoritos!</p>
      </div>
    `;
    return;
  }

  console.log(`📋 [MEMBER] Renderizando ${prompts.length} prompts`);

  container.innerHTML = prompts
    .map((prompt, index) => {
      console.log(`📄 [MEMBER] Prompt ${index + 1}:`, prompt.title);
      return `
    <div class="card mb-3">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">${prompt.title || "Sem título"}</h6>
        <small class="text-muted">${
          prompt.created_at
            ? new Date(prompt.created_at).toLocaleDateString()
            : "Data não disponível"
        }</small>
      </div>
      <div class="card-body">
        <p class="text-muted mb-2">${prompt.context || "Sem contexto"}</p>
        <div class="prompt-content" style="max-height: 150px; overflow-y: auto;">
          ${prompt.content || "Conteúdo não disponível"}
        </div>
        <div class="mt-2">
          <span class="badge bg-secondary me-1">${prompt.style}</span>
          <span class="badge bg-info me-1">${prompt.tone}</span>
          <span class="badge bg-success">${prompt.category}</span>
        </div>
      </div>
    </div>
    `;
    })
    .join("");
}

// Gerar prompt COSTAR com verificação de quota
async function generatePromptWithQuota(promptData) {
  try {
    showLoading(true);

    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/members/generate-prompt`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(promptData),
    });

    const data = await response.json();

    if (response.ok) {
      // Sucesso - mostrar resultado
      displayGeneratedPrompt(data);

      // Atualizar quota no dashboard
      if (data.metadata.quota_info) {
        updateQuotaDisplay(data.metadata.quota_info);
      }

      // Recarregar analytics
      loadDashboardData();

      return data;
    } else if (response.status === 429) {
      // Quota excedida
      showQuotaExceededModal(data.detail.quota_info);
      return null;
    } else {
      throw new Error(data.detail || "Erro ao gerar prompt");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro ao gerar prompt: " + error.message, "danger");
    return null;
  } finally {
    showLoading(false);
  }
}

// Exibir prompt gerado
function displayGeneratedPrompt(data) {
  const resultContainer = document.getElementById("promptResult");
  if (resultContainer) {
    resultContainer.innerHTML = `
      <div class="card">
        <div class="card-header d-flex justify-content-between">
          <h6>Prompt COSTAR Gerado</h6>
          <div>
            <button class="btn btn-sm btn-outline-primary" onclick="copyPromptToClipboard()">
              <i class="fas fa-copy"></i> Copiar
            </button>
            <button class="btn btn-sm btn-outline-success" onclick="saveGeneratedPrompt()">
              <i class="fas fa-save"></i> Salvar
            </button>
          </div>
        </div>
        <div class="card-body">
          <div id="generatedPromptText" style="white-space: pre-wrap;">${
            data.prompt_gerado
          }</div>
          <div class="mt-3 text-muted">
            <small>
              Tokens estimados: ${data.metadata.tokens_estimated} | 
              Tempo de resposta: ${data.metadata.response_time.toFixed(2)}s
            </small>
          </div>
        </div>
      </div>
    `;
  }
}

// Modal de quota excedida
function showQuotaExceededModal(quotaInfo) {
  const modalHtml = `
    <div class="modal fade" id="quotaExceededModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">
              <i class="fas fa-exclamation-triangle"></i> Quota Mensal Excedida
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Você atingiu o limite de prompts para este mês:</p>
            <ul>
              <li><strong>Usado:</strong> ${quotaInfo.used} prompts</li>
              <li><strong>Limite:</strong> ${quotaInfo.limit} prompts</li>
              <li><strong>Restante:</strong> ${quotaInfo.remaining} prompts</li>
            </ul>
            <p>Para continuar gerando prompts, considere fazer upgrade do seu plano.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
            <button type="button" class="btn btn-primary" onclick="showUpgradeModal()">
              <i class="fas fa-arrow-up"></i> Fazer Upgrade
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Adicionar modal ao DOM se não existir
  if (!document.getElementById("quotaExceededModal")) {
    document.body.insertAdjacentHTML("beforeend", modalHtml);
  }

  const modal = new bootstrap.Modal(
    document.getElementById("quotaExceededModal")
  );
  modal.show();
}

// Copiar prompt para clipboard
function copyPromptToClipboard() {
  const promptText = document.getElementById("generatedPromptText");
  if (promptText) {
    navigator.clipboard.writeText(promptText.textContent).then(() => {
      showAlert("Prompt copiado para clipboard!", "success");
    });
  }
}

// Salvar prompt gerado
async function saveGeneratedPrompt() {
  const promptText = document.getElementById("generatedPromptText");
  if (!promptText) return;

  const title = prompt("Digite um título para este prompt:");
  if (!title) return;

  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE}/members/save-prompt`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: title,
        content: promptText.textContent,
        category: "generated",
      }),
    });

    if (response.ok) {
      showAlert("Prompt salvo com sucesso!", "success");
      loadSavedPrompts(); // Recarregar lista
    } else {
      showAlert("Erro ao salvar prompt", "danger");
    }
  } catch (error) {
    console.error("Erro:", error);
    showAlert("Erro de conexão", "danger");
  }
}

// Atualizar dados quando a aba mudar (se necessário)
function initializeTabEventListeners() {
  // Event listener para mudança de abas
  document.querySelectorAll('[data-bs-toggle="tab"]').forEach((tab) => {
    tab.addEventListener("shown.bs.tab", function (event) {
      const targetId = event.target.getAttribute("data-bs-target");

      if (targetId === "#saved-prompts-tab") {
        loadSavedPrompts();
      }
    });
  });
}
