/**
 * Editor de Esqueleto de Landing Page
 * Versão simplificada e otimizada
 */

const SkeletonEditor = (function() {
  // Estado privado
  const state = {
    skeletonId: null,
    isEditMode: false,
    hasChanges: false,
    data: {},
    currentEditingField: null
  };

  // Elementos DOM
  const elements = {
    editModeToggle: null,
    editModeText: null,
    saveChangesBtn: null,
    addSectionBtn: null,
    sectionsContainer: null,
    saveChangesFooter: null
  };

  /**
   * Funções privadas
   */

  // Inicializar elementos DOM
  function initElements() {
    elements.editModeToggle = document.getElementById('editModeToggle');
    elements.editModeText = document.getElementById('editModeText');
    elements.saveChangesBtn = document.getElementById('saveChangesBtn');
    elements.addSectionBtn = document.getElementById('addSectionBtn');
    elements.sectionsContainer = document.getElementById('sectionsContainer');
    elements.saveChangesFooter = document.getElementById('saveChangesFooter');
  }

  // Vincular eventos
  function bindEvents() {
    // Eventos de campos editáveis
    document.addEventListener('click', function(e) {
      if (e.target.closest('.editable-field') && state.isEditMode) {
        editField(e.target.closest('.editable-field'));
      }
    });

    // Atalhos de teclado
    document.addEventListener('keydown', function(e) {
      // Ctrl/Cmd + E = Toggle Edit Mode
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        toggleEditMode();
      }
      
      // Ctrl/Cmd + S = Save Changes
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (state.hasChanges) {
          saveChanges();
        }
      }
      
      // Escape = Exit Edit Mode
      if (e.key === 'Escape' && state.isEditMode) {
        toggleEditMode();
      }
    });

    // Aviso antes de sair com alterações não salvas
    window.addEventListener('beforeunload', function(e) {
      if (state.hasChanges) {
        e.preventDefault();
        e.returnValue = 'Você tem alterações não salvas. Tem certeza que deseja sair?';
        return e.returnValue;
      }
    });

    // Evento para tipo de seção personalizada
    const sectionSelect = document.getElementById('newSectionName');
    if (sectionSelect) {
      sectionSelect.addEventListener('change', function() {
        const customField = document.getElementById('customNameField');
        if (this.value === 'custom') {
          customField.style.display = 'block';
        } else {
          customField.style.display = 'none';
        }
      });
    }

    if (elements.addSectionBtn) {
      elements.addSectionBtn.addEventListener('click', function() {
        addNewSection();
      });
    }
  }

  // Editar campo
  function editField(fieldElement) {
    if (!state.isEditMode) return;
    
    const currentValue = fieldElement.textContent.trim();
    const fieldType = fieldElement.dataset.field;
    const sectionIndex = fieldElement.dataset.section;
    const context = fieldElement.dataset.context;
    
    // Prevenir múltiplas edições simultâneas
    if (state.currentEditingField) {
      cancelEdit(state.currentEditingField);
    }
    
    state.currentEditingField = fieldElement;
    
    // Criar elemento de input
    const isLongField = ['description', 'style_notes', 'content_guidelines', 'value_proposition'].includes(fieldType);
    
    const input = isLongField 
      ? document.createElement('textarea')
      : document.createElement('input');
    
    input.className = 'form-control';
    
    if (isLongField) {
      input.rows = 3;
    } else {
      input.type = 'text';
    }
    
    input.value = currentValue;
    input.style.minWidth = '200px';
    
    // Substituir campo por input
    fieldElement.style.display = 'none';
    fieldElement.classList.add('editing');
    fieldElement.parentNode.insertBefore(input, fieldElement.nextSibling);
    
    // Focar e selecionar
    input.focus();
    input.select();
    
    // Eventos do input
    input.addEventListener('blur', function() {
      saveFieldEdit(fieldElement, input, fieldType, sectionIndex, context);
    });
    
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        saveFieldEdit(fieldElement, input, fieldType, sectionIndex, context);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        cancelEdit(fieldElement);
      }
    });
  }

  // Salvar edição de campo
  function saveFieldEdit(fieldElement, input, fieldType, sectionIndex, context) {
    const newValue = input.value.trim();
    const currentValue = fieldElement.textContent.trim();
    
    if (newValue !== currentValue && newValue.length > 0) {
      fieldElement.textContent = newValue;
      updateData(fieldType, newValue, sectionIndex, context);
      markAsChanged();
      showAlert('success', '✅ Campo atualizado!');
    }
    
    restoreField(fieldElement, input);
  }

  // Restaurar campo após edição
  function restoreField(fieldElement, input) {
    fieldElement.style.display = 'inline';
    fieldElement.classList.remove('editing');
    if (input && input.parentNode) {
      input.remove();
    }
    state.currentEditingField = null;
  }

  // Cancelar edição atual
  function cancelEdit(fieldElement) {
    if (fieldElement) {
      const input = fieldElement.nextSibling;
      restoreField(fieldElement, input);
    }
  }

  // Atualizar dados do esqueleto
  function updateData(fieldType, newValue, sectionIndex, context) {
    if (sectionIndex !== undefined && sectionIndex !== null) {
      // Campo de seção
      if (state.data.sections && state.data.sections[sectionIndex]) {
        state.data.sections[sectionIndex][fieldType] = newValue;
      }
    } else if (context) {
      // Campo de contexto (visual_identity, conversion_strategy, global_context)
      if (!state.data[context]) {
        state.data[context] = {};
      }
      state.data[context][fieldType] = newValue;
    }
  }

  // Marcar como alterado
  function markAsChanged() {
    state.hasChanges = true;
    elements.saveChangesBtn.classList.remove('hidden');
    elements.saveChangesFooter.classList.remove('hidden');
  }

  // Atualizar UI com base no modo de edição
  function updateUI() {
    const editOnlyElements = document.querySelectorAll('.edit-only');
    const sectionActions = document.querySelectorAll('.section-actions');
    const appContainer = document.getElementById('app');
    
    if (state.isEditMode) {
      // Ativar modo de edição
      elements.editModeToggle.classList.add('active');
      elements.editModeText.textContent = 'Desativar Edição';
      appContainer.classList.add('edit-mode');
      
      editOnlyElements.forEach(el => el.classList.remove('hidden'));
      sectionActions.forEach(action => action.classList.remove('hidden'));
      
      showAlert('info', '✏️ Modo de edição ativado! Clique nos campos para editar.');
    } else {
      // Desativar modo de edição
      elements.editModeToggle.classList.remove('active');
      elements.editModeText.textContent = 'Ativar Edição';
      appContainer.classList.remove('edit-mode');
      
      editOnlyElements.forEach(el => el.classList.add('hidden'));
      sectionActions.forEach(action => action.classList.add('hidden'));
      
      // Cancelar edição em andamento
      if (state.currentEditingField) {
        cancelEdit(state.currentEditingField);
      }
      
      // Mostrar botão de salvar se houver alterações
      if (state.hasChanges) {
        elements.saveChangesFooter.classList.remove('hidden');
        showAlert('warning', '⚠️ Você tem alterações não salvas.');
      }
    }
  }

  // Mostrar loading
  function showLoading(message = 'Processando...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = overlay.querySelector('.loading-text');
    if (text) text.textContent = message;
    overlay.classList.remove('hidden');
  }

  // Ocultar loading
  function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
  }

  // Mostrar alerta
  function showAlert(type, message, duration = 5000) {
    // Mapeamento de tipos para cores do Tailwind
    const typeClasses = {
      success: 'bg-green-100 text-green-800 border-green-200',
      error: 'bg-red-100 text-red-800 border-red-200',
      warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      info: 'bg-blue-100 text-blue-800 border-blue-200'
    };
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `rounded-md p-4 mb-4 border ${typeClasses[type] || typeClasses.info} alert-dismissible`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.maxWidth = '300px';
    
    alertDiv.innerHTML = `
      <div class="flex">
        <div class="flex-shrink-0">
          <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        </div>
        <div class="ml-3">
          <p>${message}</p>
        </div>
        <div class="ml-auto">
          <button type="button" class="text-gray-400 hover:text-gray-500" onclick="this.parentElement.parentElement.parentElement.remove()">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    `;
    
    // Inserir no body em vez de main para posicionamento fixo
    document.body.appendChild(alertDiv);
    
    // Auto-remover
    if (duration > 0) {
      setTimeout(() => {
        if (alertDiv.parentNode) {
          alertDiv.remove();
        }
      }, duration);
    }
  }

  // Regenerar seções na UI
  function rebuildSectionsUI() {
    if (!elements.sectionsContainer) return;
    
    elements.sectionsContainer.innerHTML = '';
    
    if (!state.data.sections || state.data.sections.length === 0) {
      elements.sectionsContainer.innerHTML = `
        <div class="text-center py-5 bg-gray-100 rounded-lg">
          <i class="fas fa-exclamation-triangle text-yellow-500 text-4xl mb-3"></i>
          <h3 class="text-lg font-medium">Nenhuma seção encontrada</h3>
          <p class="text-gray-600">O esqueleto não possui seções definidas.</p>
        </div>
      `;
      return;
    }
    
    state.data.sections.forEach((section, index) => {
      const sectionHTML = generateSectionHTML(section, index);
            elements.sectionsContainer.insertAdjacentHTML('beforeend', sectionHTML);
    });
    
    // Atualizar estatísticas
    updateStats();
  }

  // Gerar HTML para uma seção
  function generateSectionHTML(section, index) {
    return `
      <div class="section-card" data-section-index="${index}">
        <!-- Cabeçalho da Seção -->
        <div class="section-header">
          <div class="flex items-center flex-grow-1">
            <div class="section-order w-12 h-12 rounded-full bg-blue-800 flex items-center justify-center font-bold text-white mr-3">
              ${section.order}
            </div>
            <div class="flex-grow-1">
              <h3 class="section-title text-lg font-semibold mb-1">
                <span class="editable-field" data-field="title" data-section="${index}">
                  ${section.title}
                </span>
              </h3>
              <p class="section-description text-sm opacity-90">
                <span class="editable-field" data-field="description" data-section="${index}">
                  ${section.description}
                </span>
              </p>
            </div>
          </div>
          
          <div class="section-actions ${state.isEditMode ? '' : 'hidden'}">
            ${index > 0 ? `
              <button class="btn-icon text-white hover:bg-blue-700 p-1 rounded" onclick="SkeletonEditor.moveSection(${index}, 'up')" title="Mover para cima">
                <i class="fas fa-arrow-up"></i>
              </button>
            ` : ''}
            ${index < state.data.sections.length - 1 ? `
              <button class="btn-icon text-white hover:bg-blue-700 p-1 rounded" onclick="SkeletonEditor.moveSection(${index}, 'down')" title="Mover para baixo">
                <i class="fas fa-arrow-down"></i>
              </button>
            ` : ''}
            <button class="btn-icon text-white hover:bg-red-600 p-1 rounded" onclick="SkeletonEditor.removeSection(${index})" title="Remover seção">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
        
        <!-- Corpo da Seção -->
        <div class="section-body p-4">
          <!-- Elementos -->
          ${section.elements && section.elements.length > 0 ? `
            <div class="mb-4">
              <div class="text-sm font-semibold text-gray-600 mb-1">
                <i class="fas fa-puzzle-piece me-1"></i>
                Elementos:
              </div>
              <div class="elements-container flex flex-wrap gap-1" data-field="elements" data-section="${index}">
                ${section.elements.map(element => `
                  <span class="element-tag bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                    <i class="fas fa-cube me-1"></i>
                    ${element}
                  </span>
                `).join('')}
              </div>
              <button class="btn-sm mt-2 ${state.isEditMode ? '' : 'hidden'} edit-only px-2 py-1 text-sm bg-blue-100 text-blue-800 rounded" onclick="SkeletonEditor.editElements(${index})">
                <i class="fas fa-edit me-1"></i>
                Editar Elementos
              </button>
            </div>
          ` : ''}
          
          <!-- Notas de Estilo -->
          <div class="mb-4">
            <div class="text-sm font-semibold text-gray-600 mb-1">
              <i class="fas fa-palette me-1"></i>
              Notas de Estilo:
            </div>
            <div class="bg-gray-100 p-3 rounded">
              <span class="editable-field" data-field="style_notes" data-section="${index}">
                ${section.style_notes || 'Sem notas de estilo'}
              </span>
            </div>
          </div>
          
          <!-- Diretrizes de Conteúdo -->
          <div class="mb-2">
            <div class="text-sm font-semibold text-gray-600 mb-1">
              <i class="fas fa-file-alt me-1"></i>
              Diretrizes de Conteúdo:
            </div>
            <div class="bg-gray-100 p-3 rounded">
              <span class="editable-field" data-field="content_guidelines" data-section="${index}">
                ${section.content_guidelines || 'Sem diretrizes de conteúdo'}
              </span>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // Atualizar estatísticas
  function updateStats() {
    const sectionsCount = document.querySelector('.stats .font-bold');
    if (sectionsCount) {
      sectionsCount.textContent = state.data.sections ? state.data.sections.length : 0;
    }
  }

  /**
   * API pública
   */
  return {
    // Inicialização
    init: function(skeletonData, skeletonId) {
      console.log('🎨 Inicializando Editor de Esqueleto...');
      
      state.data = skeletonData || {};
      state.skeletonId = skeletonId;
      
      initElements();
      bindEvents();
      
      console.log('✅ Editor inicializado com sucesso!');
    },

    // Alternar modo de edição
    toggleEditMode: function() {
      state.isEditMode = !state.isEditMode;
      updateUI();
    },

    // Mover seção
    moveSection: function(index, direction) {
      if (!state.isEditMode) return;
      
      const newIndex = direction === 'up' ? index - 1 : index + 1;
      
      if (newIndex < 0 || newIndex >= state.data.sections.length) return;
      
      // Trocar seções
      [state.data.sections[index], state.data.sections[newIndex]] = 
      [state.data.sections[newIndex], state.data.sections[index]];
      
      // Atualizar números de ordem
      state.data.sections.forEach((section, i) => {
        section.order = i + 1;
      });
      
      // Reconstruir UI
      rebuildSectionsUI();
      
      markAsChanged();
      showAlert('success', '✅ Seção reordenada!');
    },

    // Remover seção
    removeSection: function(index) {
      if (!state.isEditMode) return;
      
      if (!confirm(`Tem certeza que deseja remover esta seção?`)) {
        return;
      }
      
      // Remover dos dados
      state.data.sections.splice(index, 1);
      
      // Atualizar números de ordem
      state.data.sections.forEach((section, i) => {
        section.order = i + 1;
      });
      
      // Reconstruir UI
      rebuildSectionsUI();
      
      markAsChanged();
      showAlert('success', '✅ Seção removida!');
    },

    // Adicionar nova seção
    addNewSection: function() {
      if (!state.isEditMode) return;
      
      const modal = document.getElementById('addSectionModal');
      new bootstrap.Modal(modal).show();
    },

    // Salvar nova seção
    saveNewSection: function() {
      const sectionName = document.getElementById('newSectionName').value;
      const customName = document.getElementById('customSectionName').value;
      const title = document.getElementById('newSectionTitle').value;
      const description = document.getElementById('newSectionDescription').value;
      
      if (!title.trim()) {
        showAlert('error', '❌ Título da seção é obrigatório!');
        return;
      }
      
      const finalName = sectionName === 'custom' ? customName : sectionName;
      
      if (sectionName === 'custom' && !customName.trim()) {
        showAlert('error', '❌ Nome personalizado é obrigatório!');
        return;
      }
      
      // Criar nova seção
      const newSection = {
        name: finalName,
        order: state.data.sections ? state.data.sections.length + 1 : 1,
        title: title.trim(),
        description: description.trim() || 'Nova seção adicionada pelo usuário',
        elements: ['conteúdo', 'layout'],
        style_notes: 'Estilo a ser definido',
        content_guidelines: 'Conteúdo a ser desenvolvido'
      };
      
      // Adicionar aos dados
      if (!state.data.sections) {
        state.data.sections = [];
      }
      
      state.data.sections.push(newSection);
      
      // Reconstruir UI
      rebuildSectionsUI();
      
      markAsChanged();
      bootstrap.Modal.getInstance(document.getElementById('addSectionModal')).hide();
      showAlert('success', `✅ Seção "${title}" adicionada com sucesso!`);
      
      // Limpar formulário
      document.getElementById('newSectionTitle').value = '';
      document.getElementById('newSectionDescription').value = '';
      document.getElementById('customSectionName').value = '';
    },

    // Editar cor
    editColor: function(colorType, currentColor) {
      if (!state.isEditMode) {
        showAlert('warning', '⚠️ Ative o modo de edição para alterar cores.');
        return;
      }
      
      const modal = document.getElementById('colorModal');
      const colorTypeSpan = document.getElementById('colorType');
      const colorPicker = document.getElementById('colorPicker');
      const colorHex = document.getElementById('colorHex');
      const colorPreview = document.getElementById('colorPreview');
      
      // Configurar modal
      const typeNames = {
        'primary': 'Primária',
        'secondary': 'Secundária',
        'accent': 'Destaque'
      };
      
      colorTypeSpan.textContent = typeNames[colorType] || colorType;
      colorPicker.value = currentColor;
      colorHex.value = currentColor;
      colorPreview.style.background = currentColor;
      
      // Armazenar tipo atual
      modal.dataset.colorType = colorType;
      
      // Sincronizar picker e hex
      const syncColors = () => {
        colorHex.value = colorPicker.value;
        colorPreview.style.background = colorPicker.value;
      };
      
      colorPicker.addEventListener('input', syncColors);
      
      // Mostrar modal
      new bootstrap.Modal(modal).show();
    },

    // Salvar cor
    saveColor: function() {
      const modal = document.getElementById('colorModal');
      const colorType = modal.dataset.colorType;
      const newColor = document.getElementById('colorHex').value;
      
      if (!/^#[0-9A-Fa-f]{6}$/.test(newColor)) {
        showAlert('error', '❌ Cor inválida! Use o formato #RRGGBB');
        return;
      }
      
      // Atualizar dados
      if (!state.data.visual_identity) {
        state.data.visual_identity = {};
      }
      state.data.visual_identity[colorType + '_color'] = newColor;
      
      // Atualizar UI
      const colorPreview = document.querySelector(`[onclick*="${colorType}"]`);
      const colorValue = document.querySelector(`[data-field="${colorType}_color"]`);
      
      if (colorPreview) {
        colorPreview.style.background = newColor;
      }
      if (colorValue) {
        colorValue.textContent = newColor;
      }
      
      markAsChanged();
      bootstrap.Modal.getInstance(modal).hide();
      showAlert('success', `✅ Cor ${colorType} atualizada para ${newColor}!`);
    },

    // Editar elementos
    editElements: function(sectionIndex) {
      if (!state.isEditMode) return;
      
      const modal = document.getElementById('elementsModal');
      const textarea = document.getElementById('elementsTextarea');
      
      const elements = state.data.sections[sectionIndex].elements || [];
      textarea.value = elements.join('\n');
      
      // Armazenar índice da seção
      modal.dataset.sectionIndex = sectionIndex;
      
      new bootstrap.Modal(modal).show();
    },

    // Salvar elementos
    saveElements: function() {
      const modal = document.getElementById('elementsModal');
      const sectionIndex = parseInt(modal.dataset.sectionIndex);
      const elementsText = document.getElementById('elementsTextarea').value;
      
      const elements = elementsText.split('\n')
                                  .map(el => el.trim())
                                  .filter(el => el.length > 0);
      
      if (sectionIndex >= 0 && state.data.sections[sectionIndex]) {
        state.data.sections[sectionIndex].elements = elements;
        
        // Reconstruir UI
        rebuildSectionsUI();
        
        markAsChanged();
        bootstrap.Modal.getInstance(modal).hide();
        showAlert('success', '✅ Elementos atualizados!');
      }
    },

    // Editar elementos de confiança
    editTrustElements: function() {
      if (!state.isEditMode) return;
      
      const elements = state.data.conversion_strategy?.trust_elements || [];
      
      const modal = document.getElementById('elementsModal');
      const modalTitle = modal.querySelector('.modal-title');
      const textarea = document.getElementById('elementsTextarea');
      
      modalTitle.innerHTML = '<i class="fas fa-shield-alt me-2"></i>Elementos de Confiança';
      textarea.value = elements.join('\n');
      
      // Configurar callback personalizado
      modal.dataset.customType = 'trust_elements';
      
      new bootstrap.Modal(modal).show();
    },

    // Salvar elementos personalizados
    saveCustomElements: function() {
      const modal = document.getElementById('elementsModal');
      const customType = modal.dataset.customType;
      const elementsText = document.getElementById('elementsTextarea').value;
      
      const elements = elementsText.split('\n')
                                  .map(el => el.trim())
                                  .filter(el => el.length > 0);
      
      if (customType === 'trust_elements') {
        if (!state.data.conversion_strategy) {
          state.data.conversion_strategy = {};
        }
        state.data.conversion_strategy.trust_elements = elements;
        
                // Atualizar UI
        const container = document.querySelector('[data-field="trust_elements"]');
        if (container) {
          container.innerHTML = elements.map(el => `
            <span class="element-tag bg-white/20 text-white text-xs px-2 py-1 rounded-full">
              <i class="fas fa-shield-alt me-1"></i>
              ${el}
            </span>
          `).join('');
        }
      }
      
      markAsChanged();
      bootstrap.Modal.getInstance(modal).hide();
      showAlert('success', '✅ Elementos atualizados!');
    },
    
    // Salvar alterações
    saveChanges: async function() {
      if (!state.hasChanges) {
        showAlert('info', 'ℹ️ Não há alterações para salvar.');
        return;
      }
      
      if (!confirm('💾 Deseja salvar todas as alterações feitas no esqueleto?')) {
        return;
      }
      
      showLoading('Salvando alterações...');
      
      try {
        const response = await fetch(`/update-skeleton/${state.skeletonId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            skeleton_data: state.data
          })
        });
        
        const result = await response.json();
        
        if (result.success) {
          state.hasChanges = false;
          elements.saveChangesBtn.classList.add('hidden');
          elements.saveChangesFooter.classList.add('hidden');
          
          showAlert('success', '✅ ' + result.message);
          
          // Recarregar página após 2 segundos
          setTimeout(() => {
            location.reload();
          }, 2000);
        } else {
          showAlert('error', '❌ ' + (result.error || 'Erro ao salvar alterações'));
        }
      } catch (error) {
        console.error('Erro:', error);
        showAlert('error', '❌ Erro de conexão ao salvar alterações.');
      } finally {
        hideLoading();
      }
    },
    
    // Regenerar esqueleto
    regenerateSkeleton: async function() {
      if (state.hasChanges) {
        if (!confirm('⚠️ Você tem alterações não salvas que serão perdidas. Deseja continuar mesmo assim?')) {
          return;
        }
      }
      
      if (!confirm('🔄 Deseja regenerar o esqueleto? Isso substituirá completamente o esqueleto atual.')) {
        return;
      }
      
      showLoading('Regenerando esqueleto...');
      
      try {
        const response = await fetch(`/regenerate-skeleton/${state.skeletonId}`, {
          method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
          showAlert('success', '✅ ' + result.message);
          setTimeout(() => {
            window.location.href = result.redirect_url;
          }, 1500);
        } else {
          showAlert('error', '❌ ' + (result.error || 'Erro ao regenerar esqueleto'));
        }
      } catch (error) {
        console.error('Erro:', error);
        showAlert('error', '❌ Erro de conexão ao regenerar esqueleto.');
      } finally {
        hideLoading();
      }
    },
    
    // Gerar Hero Section
    generateHeroSection: function() {
      if (state.hasChanges) {
        if (!confirm('⚠️ Você tem alterações não salvas. Deseja salvar antes de continuar?')) {
          return;
        }
        this.saveChanges();
        return;
      }
      
      if (confirm('🚀 Deseja gerar a Hero Section baseada neste esqueleto?')) {
        showAlert('info', '🚧 Funcionalidade em desenvolvimento!');
        // Implementação futura
      }
    }
  };
})();

// Funções globais para compatibilidade com onclick inline
function toggleEditMode() {
  SkeletonEditor.toggleEditMode();
}

function addNewSection() {
  SkeletonEditor.addNewSection();
}

function saveNewSection() {
  SkeletonEditor.saveNewSection();
}

function editColor(colorType, currentColor) {
  SkeletonEditor.editColor(colorType, currentColor);
}

function saveColor() {
  SkeletonEditor.saveColor();
}

function editElements(sectionIndex) {
  SkeletonEditor.editElements(sectionIndex);
}

function saveElements() {
  SkeletonEditor.saveElements();
}

function editTrustElements() {
  SkeletonEditor.editTrustElements();
}

function saveCustomElements() {
  SkeletonEditor.saveCustomElements();
}

function saveChanges() {
  SkeletonEditor.saveChanges();
}

function regenerateSkeleton() {
  SkeletonEditor.regenerateSkeleton();
}

function generateHeroSection() {
  SkeletonEditor.generateHeroSection();
}
