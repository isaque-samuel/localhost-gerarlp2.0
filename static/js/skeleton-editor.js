/**
 * Editor de Esqueleto de Landing Page
 * Sistema de edição inline para esqueletos gerados por IA
 */

const SkeletonEditor = {
    // Configurações
    config: {
        skeletonId: null,
        isEditMode: false,
        hasChanges: false,
        autoSaveInterval: 30000, // 30 segundos
        currentEditingField: null
    },
    
    // Dados do esqueleto
    data: {},
    
    // Elementos DOM
    elements: {
        editModeToggle: null,
        editModeText: null,
        saveChangesBtn: null,
        addSectionBtn: null,
        sectionsContainer: null
    },
    
    /**
     * Inicializar o editor
     */
    init(skeletonData, skeletonId) {
        console.log('🎨 Inicializando Editor de Esqueleto...');
        
        this.data = skeletonData || {};
        this.config.skeletonId = skeletonId;
        
        this.initElements();
        this.bindEvents();
        this.initAutoSave();
        this.loadDraft();
        
        console.log('✅ Editor inicializado com sucesso!');
    },
    
    /**
     * Inicializar elementos DOM
     */
    initElements() {
        this.elements.editModeToggle = document.getElementById('editModeToggle');
        this.elements.editModeText = document.getElementById('editModeText');
        this.elements.saveChangesBtn = document.getElementById('saveChangesBtn');
        this.elements.addSectionBtn = document.getElementById('addSectionBtn');
        this.elements.sectionsContainer = document.getElementById('sectionsContainer');
    },
    
    /**
     * Vincular eventos
     */
    bindEvents() {
        // Eventos de campos editáveis
        document.addEventListener('click', (e) => {
            if (e.target.closest('.editable-field') && this.config.isEditMode) {
                this.editField(e.target.closest('.editable-field'));
            }
        });
        
        // Atalhos de teclado
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + E = Toggle Edit Mode
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                e.preventDefault();
                this.toggleEditMode();
            }
            
            // Ctrl/Cmd + S = Save Changes
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                if (this.config.hasChanges) {
                    this.saveChanges();
                }
            }
            
            // Escape = Exit Edit Mode
            if (e.key === 'Escape' && this.config.isEditMode) {
                this.toggleEditMode();
            }
        });
        
        // Aviso antes de sair com alterações não salvas
        window.addEventListener('beforeunload', (e) => {
            if (this.config.hasChanges) {
                e.preventDefault();
                e.returnValue = 'Você tem alterações não salvas. Tem certeza que deseja sair?';
                return e.returnValue;
            }
        });
    },
    
    /**
     * Alternar modo de edição
     */
    toggleEditMode() {
        this.config.isEditMode = !this.config.isEditMode;
        
        const toggle = this.elements.editModeToggle;
        const text = this.elements.editModeText;
        const editOnlyElements = document.querySelectorAll('.edit-only');
        const sectionActions = document.querySelectorAll('.section-actions');
        const addSectionBtn = this.elements.addSectionBtn;
        
        if (this.config.isEditMode) {
            // Ativar modo de edição
            toggle.classList.add('active');
            text.textContent = 'Sair da Edição';
            
            editOnlyElements.forEach(el => el.classList.remove('d-none'));
            sectionActions.forEach(action => action.classList.remove('d-none'));
            addSectionBtn.classList.remove('d-none');
            
            // Adicionar estilos de edição
            document.querySelectorAll('.editable-field').forEach(field => {
                field.style.cursor = 'pointer';
            });
            
            // Mostrar botão de salvar no footer se estiver em modo de edição
            const saveFooter = document.getElementById('saveChangesFooter');
            if (saveFooter) {
                saveFooter.classList.remove('d-none');
            }
            
            this.showAlert('info', '✏️ Modo de edição ativado! Clique nos campos para editar.');
        } else {
            // Desativar modo de edição
            toggle.classList.remove('active');
            text.textContent = 'Ativar Edição';
            
            editOnlyElements.forEach(el => el.classList.add('d-none'));
            sectionActions.forEach(action => action.classList.add('d-none'));
            addSectionBtn.classList.add('d-none');
            
            // Remover estilos de edição
            document.querySelectorAll('.editable-field').forEach(field => {
                field.style.cursor = 'default';
                field.classList.remove('editing');
            });
            
            // Ocultar botão de salvar no footer quando sair do modo de edição
            const saveFooter = document.getElementById('saveChangesFooter');
            if (saveFooter) {
                saveFooter.classList.add('d-none');
            }
            
            // Mostrar botão de salvar se houver alterações
            if (this.config.hasChanges) {
                document.getElementById('saveChangesFooter').classList.remove('d-none');
                this.showAlert('warning', '⚠️ Você tem alterações não salvas. Clique em "Salvar Alterações" para manter as mudanças.');
            }
        }
    },
    
    /**
     * Editar campo
     */
    editField(fieldElement) {
        if (!this.config.isEditMode) return;
        
        const currentValue = fieldElement.textContent.trim();
        const fieldType = fieldElement.dataset.field;
        const sectionIndex = fieldElement.dataset.section;
        const context = fieldElement.dataset.context;
        
        // Prevenir múltiplas edições simultâneas
        if (this.config.currentEditingField) {
            this.cancelEdit(this.config.currentEditingField);
        }
        
        this.config.currentEditingField = fieldElement;
        
        // Criar elemento de input
        let input;
        if (this.isLongTextField(fieldType)) {
            input = document.createElement('textarea');
            input.className = 'form-control';
            input.rows = 3;
        } else {
            input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-control';
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
        const saveEdit = () => {
            const newValue = input.value.trim();
            if (newValue !== currentValue && newValue.length > 0) {
                fieldElement.textContent = newValue;
                this.updateData(fieldType, newValue, sectionIndex, context);
                this.markAsChanged();
                this.showAlert('success', '✅ Campo atualizado!');
            }
            this.restoreField(fieldElement, input);
        };
        
        const cancelEdit = () => {
            this.restoreField(fieldElement, input);
        };
        
        // Event listeners
        input.addEventListener('blur', saveEdit);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                saveEdit();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelEdit();
            }
        });
    },
    
    /**
     * Restaurar campo após edição
     */
    restoreField(fieldElement, input) {
        fieldElement.style.display = 'inline';
        fieldElement.classList.remove('editing');
        if (input && input.parentNode) {
            input.remove();
        }
        this.config.currentEditingField = null;
    },
    
    /**
     * Cancelar edição atual
     */
    cancelEdit(fieldElement) {
        if (fieldElement) {
            const input = fieldElement.nextSibling;
            this.restoreField(fieldElement, input);
        }
    },
    
    /**
     * Verificar se é campo de texto longo
     */
    isLongTextField(fieldType) {
        const longFields = ['description', 'style_notes', 'content_guidelines', 'value_proposition'];
        return longFields.includes(fieldType);
    },
    
    /**
     * Atualizar dados do esqueleto
     */
    updateData(fieldType, newValue, sectionIndex, context) {
        if (sectionIndex !== undefined && sectionIndex !== null) {
            // Campo de seção
                        if (this.data.sections && this.data.sections[sectionIndex]) {
                this.data.sections[sectionIndex][fieldType] = newValue;
            }
        } else if (context) {
            // Campo de contexto (visual_identity, conversion_strategy, global_context)
            if (!this.data[context]) {
                this.data[context] = {};
            }
            this.data[context][fieldType] = newValue;
        }
        
        console.log('📝 Dados atualizados:', { fieldType, newValue, sectionIndex, context });
    },
    
    /**
     * Marcar como alterado
     */
    markAsChanged() {
        this.config.hasChanges = true;
        if (!this.config.isEditMode) {
            this.elements.saveChangesBtn.classList.remove('d-none');
        }
    },
    
    /**
     * Editar cor
     */
    editColor(colorType, currentColor) {
        if (!this.config.isEditMode) {
            this.showAlert('warning', '⚠️ Ative o modo de edição para alterar cores.');
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
            const pickerValue = colorPicker.value;
            const hexValue = colorHex.value;
            
            if (pickerValue !== hexValue && /^#[0-9A-Fa-f]{6}$/.test(hexValue)) {
                colorPicker.value = hexValue;
                colorPreview.style.background = hexValue;
            } else if (pickerValue !== hexValue) {
                colorHex.value = pickerValue;
                colorPreview.style.background = pickerValue;
            }
        };
        
        colorPicker.addEventListener('input', syncColors);
        colorHex.addEventListener('input', syncColors);
        
        // Mostrar modal
        new bootstrap.Modal(modal).show();
    },
    
    /**
     * Salvar cor
     */
    saveColor() {
        const modal = document.getElementById('colorModal');
        const colorType = modal.dataset.colorType;
        const newColor = document.getElementById('colorHex').value;
        
        if (!/^#[0-9A-Fa-f]{6}$/.test(newColor)) {
            this.showAlert('danger', '❌ Cor inválida! Use o formato #RRGGBB');
            return;
        }
        
        // Atualizar dados
        if (!this.data.visual_identity) {
            this.data.visual_identity = {};
        }
        this.data.visual_identity[colorType + '_color'] = newColor;
        
        // Atualizar UI
        const colorPreview = document.querySelector(`[onclick*="${colorType}"]`);
        const colorValue = document.querySelector(`[data-field="${colorType}_color"]`);
        
        if (colorPreview) {
            colorPreview.style.background = newColor;
        }
        if (colorValue) {
            colorValue.textContent = newColor;
        }
        
        this.markAsChanged();
        bootstrap.Modal.getInstance(modal).hide();
        this.showAlert('success', `✅ Cor ${colorType} atualizada para ${newColor}!`);
    },
    
    /**
     * Editar elementos de seção
     */
    editElements(sectionIndex) {
        if (!this.config.isEditMode) return;
        
        const modal = document.getElementById('elementsModal');
        const textarea = document.getElementById('elementsTextarea');
        
        const elements = this.data.sections[sectionIndex].elements || [];
        textarea.value = elements.join('\n');
        
        // Armazenar índice da seção
        modal.dataset.sectionIndex = sectionIndex;
        
        new bootstrap.Modal(modal).show();
    },
    
    /**
     * Salvar elementos
     */
    saveElements() {
        const modal = document.getElementById('elementsModal');
        const sectionIndex = parseInt(modal.dataset.sectionIndex);
        const elementsText = document.getElementById('elementsTextarea').value;
        
        const elements = elementsText.split('\n')
                                    .map(el => el.trim())
                                    .filter(el => el.length > 0);
        
        if (sectionIndex >= 0 && this.data.sections[sectionIndex]) {
            this.data.sections[sectionIndex].elements = elements;
            
            // Atualizar UI
            const container = document.querySelector(`[data-field="elements"][data-section="${sectionIndex}"]`);
            if (container) {
                container.innerHTML = elements.map(el => 
                    `<span class="element-tag">
                        <i class="fas fa-cube me-1"></i>
                        ${el}
                    </span>`
                ).join('');
            }
            
            this.markAsChanged();
            bootstrap.Modal.getInstance(modal).hide();
            this.showAlert('success', '✅ Elementos atualizados!');
        }
    },
    
    /**
     * Editar elementos de confiança
     */
    editTrustElements() {
        this.editStrategyElements('trust_elements', 'Elementos de Confiança');
    },
    
    /**
     * Editar elementos de urgência
     */
    editUrgencyElements() {
        this.editStrategyElements('urgency_elements', 'Elementos de Urgência');
    },
    
    /**
     * Editar objetivos secundários
     */
    editSecondaryGoals() {
        this.editContextElements('secondary_goals', 'Objetivos Secundários');
    },
    
    /**
     * Editar elementos de estratégia
     */
    editStrategyElements(fieldType, title) {
        if (!this.config.isEditMode) return;
        
        const elements = this.data.conversion_strategy?.[fieldType] || [];
        this.showElementsModal(elements, title, (newElements) => {
            if (!this.data.conversion_strategy) {
                this.data.conversion_strategy = {};
            }
            this.data.conversion_strategy[fieldType] = newElements;
            this.updateStrategyElementsUI(fieldType, newElements);
        });
    },
    
    /**
     * Editar elementos de contexto
     */
    editContextElements(fieldType, title) {
        if (!this.config.isEditMode) return;
        
        const elements = this.data.global_context?.[fieldType] || [];
        this.showElementsModal(elements, title, (newElements) => {
            if (!this.data.global_context) {
                this.data.global_context = {};
            }
            this.data.global_context[fieldType] = newElements;
            this.updateContextElementsUI(fieldType, newElements);
        });
    },
    
    /**
     * Mostrar modal de elementos genérico
     */
    showElementsModal(elements, title, onSave) {
        const modal = document.getElementById('elementsModal');
        const modalTitle = modal.querySelector('.modal-title');
        const textarea = document.getElementById('elementsTextarea');
        
        modalTitle.innerHTML = `<i class="fas fa-edit me-2"></i>${title}`;
        textarea.value = elements.join('\n');
        
        // Remover listeners anteriores
        const newModal = modal.cloneNode(true);
        modal.parentNode.replaceChild(newModal, modal);
        
        // Adicionar novo listener
        newModal.querySelector('[onclick="saveElements()"]').onclick = () => {
            const elementsText = newModal.querySelector('#elementsTextarea').value;
            const newElements = elementsText.split('\n')
                                          .map(el => el.trim())
                                          .filter(el => el.length > 0);
            
            onSave(newElements);
            this.markAsChanged();
            bootstrap.Modal.getInstance(newModal).hide();
            this.showAlert('success', `✅ ${title} atualizados!`);
        };
        
        new bootstrap.Modal(newModal).show();
    },
    
    /**
     * Atualizar UI dos elementos de estratégia
     */
    updateStrategyElementsUI(fieldType, elements) {
        const container = document.querySelector(`[data-field="${fieldType}"][data-context="conversion_strategy"]`);
        if (container) {
            const iconMap = {
                'trust_elements': 'fas fa-shield-alt',
                'urgency_elements': 'fas fa-clock'
            };
            
            container.innerHTML = elements.map(el => 
                `<span class="element-tag">
                    <i class="${iconMap[fieldType]} me-1"></i>
                    ${el}
                </span>`
            ).join('');
        }
    },
    
    /**
     * Atualizar UI dos elementos de contexto
     */
    updateContextElementsUI(fieldType, elements) {
        const container = document.querySelector(`[data-field="${fieldType}"][data-context="global_context"]`);
        if (container) {
            container.innerHTML = elements.map(el => 
                `<span class="element-tag">
                    <i class="fas fa-target me-1"></i>
                    ${el}
                </span>`
            ).join('');
        }
    },
    
    /**
     * Adicionar nova seção
     */
    addNewSection() {
        if (!this.config.isEditMode) return;
        
        const modal = document.getElementById('addSectionModal');
        const sectionSelect = document.getElementById('newSectionName');
        const customField = document.getElementById('customNameField');
        const titleField = document.getElementById('newSectionTitle');
        
        // Configurar evento de mudança do select
        sectionSelect.onchange = function() {
            if (this.value === 'custom') {
                customField.style.display = 'block';
                titleField.value = '';
            } else {
                customField.style.display = 'none';
                
                const titles = {
                    'about': 'Sobre Nós',
                    'services': 'Nossos Serviços',
                    'benefits': 'Benefícios',
                    'testimonials': 'Depoimentos',
                    'pricing': 'Preços e Planos',
                    'faq': 'Perguntas Frequentes',
                    'team': 'Nossa Equipe',
                    'portfolio': 'Portfólio',
                    'contact': 'Entre em Contato'
                };
                
                titleField.value = titles[this.value] || '';
            }
        };
        
        new bootstrap.Modal(modal).show();
    },
    
    /**
     * Salvar nova seção
     */
    saveNewSection() {
        const sectionName = document.getElementById('newSectionName').value;
        const customName = document.getElementById('customSectionName').value;
        const title = document.getElementById('newSectionTitle').value;
        const description = document.getElementById('newSectionDescription').value;
        
        if (!title.trim()) {
            this.showAlert('danger', '❌ Título da seção é obrigatório!');
            return;
        }
        
        const finalName = sectionName === 'custom' ? customName : sectionName;
        
        if (!finalName.trim()) {
            this.showAlert('danger', '❌ Nome da seção é obrigatório!');
            return;
        }
        
        // Criar nova seção
        const newSection = {
            name: finalName,
            order: this.data.sections.length + 1,
            title: title.trim(),
            description: description.trim() || 'Nova seção adicionada pelo usuário',
            elements: ['content', 'layout'],
            style_notes: 'Estilo a ser definido',
            content_guidelines: 'Conteúdo a ser desenvolvido'
        };
        
        // Adicionar aos dados
        if (!this.data.sections) {
            this.data.sections = [];
        }
        this.data.sections.push(newSection);
        
        // Adicionar à UI
        this.addSectionToUI(newSection, this.data.sections.length - 1);
        
        this.markAsChanged();
        bootstrap.Modal.getInstance(document.getElementById('addSectionModal')).hide();
        this.showAlert('success', `✅ Seção "${title}" adicionada com sucesso!`);
        
        // Limpar formulário
        document.getElementById('newSectionTitle').value = '';
        document.getElementById('newSectionDescription').value = '';
        document.getElementById('customSectionName').value = '';
    },
    
    /**
     * Adicionar seção à UI
     */
    addSectionToUI(section, index) {
        const container = this.elements.sectionsContainer;
        const sectionHTML = this.generateSectionHTML(section, index);
        
        container.insertAdjacentHTML('beforeend', sectionHTML);
        
        // Adicionar event listeners aos novos campos editáveis
        const newCard = container.lastElementChild;
        this.bindSectionEvents(newCard);
        
        // Atualizar estatísticas
        this.updateStats();
    },
    
    /**
     * Gerar HTML da seção
     */
    generateSectionHTML(section, index) {
        return `
            <div class="section-card" data-section-index="${index}">
                <div class="section-header">
                    <div class="d-flex align-items-center flex-grow-1">
                        <div class="section-order">${section.order}</div>
                        <div class="flex-grow-1">
                            <h4 class="section-title">
                                <span class="editable-field" data-field="title" data-section="${index}">
                                    ${section.title}
                                    <span class="edit-indicator"><i class="fas fa-edit"></i></span>
                                </span>
                            </h4>
                            <p class="section-description">
                                <span class="editable-field" data-field="description" data-section="${index}">
                                    ${section.description}
                                    <span class="edit-indicator"><i class="fas fa-edit"></i></span>
                                </span>
                            </p>
                        </div>
                    </div>
                    
                    <div class="section-actions ${this.config.isEditMode ? '' : 'd-none'}">
                        <div class="btn-group" role="group">
                            ${index > 0 ? `
                                                        <button class="btn btn-outline-primary btn-sm" onclick="SkeletonEditor.moveSection(${index}, 'up')" title="Mover para cima">
                                <i class="fas fa-arrow-up"></i>
                            </button>
                            ` : ''}
                            ${index < this.data.sections.length - 1 ? `
                            <button class="btn btn-outline-primary btn-sm" onclick="SkeletonEditor.moveSection(${index}, 'down')" title="Mover para baixo">
                                <i class="fas fa-arrow-down"></i>
                            </button>
                            ` : ''}
                            <button class="btn btn-outline-danger btn-sm" onclick="SkeletonEditor.removeSection(${index})" title="Remover seção">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="section-body">
                    <div class="field-group">
                        <div class="field-label">
                            <i class="fas fa-puzzle-piece"></i>
                            Elementos:
                        </div>
                        <div class="elements-container" data-field="elements" data-section="${index}">
                            ${section.elements.map(el => `
                                <span class="element-tag">
                                    <i class="fas fa-cube me-1"></i>
                                    ${el}
                                </span>
                            `).join('')}
                        </div>
                        <button class="btn btn-outline-primary btn-sm mt-2 ${this.config.isEditMode ? '' : 'd-none'} edit-only" onclick="SkeletonEditor.editElements(${index})">
                            <i class="fas fa-edit me-1"></i>
                            Editar Elementos
                        </button>
                    </div>
                    
                    <div class="field-group">
                        <div class="field-label">
                            <i class="fas fa-palette"></i>
                            Notas de Estilo:
                        </div>
                        <div class="bg-light p-3 rounded">
                            <span class="editable-field" data-field="style_notes" data-section="${index}">
                                ${section.style_notes}
                                <span class="edit-indicator"><i class="fas fa-edit"></i></span>
                            </span>
                        </div>
                    </div>
                    
                    <div class="field-group">
                        <div class="field-label">
                            <i class="fas fa-file-alt"></i>
                            Diretrizes de Conteúdo:
                        </div>
                        <div class="bg-light p-3 rounded">
                            <span class="editable-field" data-field="content_guidelines" data-section="${index}">
                                ${section.content_guidelines}
                                <span class="edit-indicator"><i class="fas fa-edit"></i></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    /**
     * Vincular eventos da seção
     */
    bindSectionEvents(sectionElement) {
        const editableFields = sectionElement.querySelectorAll('.editable-field');
        editableFields.forEach(field => {
            if (this.config.isEditMode) {
                field.style.cursor = 'pointer';
            }
        });
    },
    
    /**
     * Mover seção
     */
    moveSection(index, direction) {
        if (!this.config.isEditMode) return;
        
        const newIndex = direction === 'up' ? index - 1 : index + 1;
        
        if (newIndex < 0 || newIndex >= this.data.sections.length) return;
        
        // Trocar seções
        [this.data.sections[index], this.data.sections[newIndex]] = 
        [this.data.sections[newIndex], this.data.sections[index]];
        
        // Atualizar números de ordem
        this.data.sections.forEach((section, i) => {
        section.order = i + 1;
    });
        
        // Reconstruir UI
        this.rebuildSectionsUI();
        
        this.markAsChanged();
        this.showAlert('success', '✅ Seção reordenada!');
    },
    
    /**
     * Remover seção
     */
    removeSection(index) {
        if (!this.config.isEditMode) return;
        
        const section = this.data.sections[index];
        
        if (confirm(`🗑️ Tem certeza que deseja remover a seção "${section.title}"?\n\nEsta ação não pode ser desfeita.`)) {
            // Remover dos dados
            this.data.sections.splice(index, 1);
            
            // Atualizar números de ordem
            this.data.sections.forEach((section, i) => {
                section.order = i + 1;
            });
            
            // Reconstruir UI
            this.rebuildSectionsUI();
            
            this.markAsChanged();
            this.showAlert('success', `✅ Seção "${section.title}" removida!`);
        }
    },
    
    /**
     * Reconstruir UI das seções
     */
    rebuildSectionsUI() {
        const container = this.elements.sectionsContainer;
        container.innerHTML = '';
        
        this.data.sections.forEach((section, index) => {
            this.addSectionToUI(section, index);
        });
        
        this.updateStats();
    },
    
    /**
     * Atualizar estatísticas
     */
    updateStats() {
        const sectionsCount = document.querySelector('.stats .fs-4');
        if (sectionsCount) {
            sectionsCount.textContent = this.data.sections ? this.data.sections.length : 0;
        }
    },
    
    /**
     * Salvar alterações
     */
    async saveChanges() {
        if (!this.config.hasChanges) {
            this.showAlert('info', 'ℹ️ Não há alterações para salvar.');
            return;
        }
        
        if (!confirm('💾 Deseja salvar todas as alterações feitas no esqueleto?')) {
            return;
        }
        
        this.showLoading('Salvando alterações...');
        
        try {
            const response = await fetch(`/update-skeleton/${this.config.skeletonId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    skeleton_data: this.data
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.config.hasChanges = false;
                this.elements.saveChangesBtn.classList.add('d-none');
                const saveFooter = document.getElementById('saveChangesFooter');
                if (saveFooter) {
                    saveFooter.classList.add('d-none');
                }
                this.clearDraft();
                this.showAlert('success', '✅ ' + result.message);
                
                // Recarregar página após 2 segundos
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                this.showAlert('danger', '❌ ' + (result.error || 'Erro ao salvar alterações'));
            }
        } catch (error) {
            console.error('Erro:', error);
            this.showAlert('danger', '❌ Erro de conexão ao salvar alterações.');
        } finally {
            this.hideLoading();
        }
    },
    
    /**
     * Regenerar esqueleto
     */
    async regenerateSkeleton() {
        if (this.config.hasChanges) {
            if (!confirm('⚠️ Você tem alterações não salvas que serão perdidas.\n\nDeseja continuar mesmo assim?')) {
                return;
            }
        }
        
        if (!confirm('🔄 Deseja regenerar o esqueleto?\n\nIsso criará uma nova versão baseada no briefing original e substituirá o atual.')) {
            return;
        }
        
        const btn = event.target.closest('button');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Regenerando...';
        btn.disabled = true;
        
        this.showAlert('info', '🔄 Regenerando esqueleto... Isso pode levar alguns segundos.');
        
        try {
            const response = await fetch(`/regenerate-skeleton/${this.config.skeletonId}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('success', '✅ ' + result.message);
                setTimeout(() => {
                    window.location.href = result.redirect_url;
                }, 2000);
            } else {
                this.showAlert('danger', '❌ ' + (result.error || 'Erro ao regenerar esqueleto'));
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        } catch (error) {
            console.error('Erro:', error);
            this.showAlert('danger', '❌ Erro de conexão ao regenerar esqueleto.');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },
    
    /**
     * Gerar Hero Section
     */
    generateHeroSection() {
        if (this.config.hasChanges) {
            if (!confirm('⚠️ Você tem alterações não salvas.\n\nDeseja salvar antes de continuar para a Hero Section?')) {
                return;
            }
            this.saveChanges();
            return;
        }
        
        if (confirm('🎨 Deseja gerar a Hero Section baseada neste esqueleto?\n\nIsso iniciará a próxima fase do desenvolvimento.')) {
            this.showAlert('info', '🚧 Funcionalidade será implementada na Fase 3!');
            // TODO: Implementar na Fase 3
        }
    },
    
    /**
     * Auto-save (rascunho)
     */
    initAutoSave() {
        setInterval(() => {
            if (this.config.hasChanges && this.config.isEditMode) {
                this.saveDraft();
            }
        }, this.config.autoSaveInterval);
    },
    
    /**
     * Salvar rascunho
     */
    saveDraft() {
        try {
            localStorage.setItem(`skeleton_draft_${this.config.skeletonId}`, JSON.stringify({
                data: this.data,
                timestamp: new Date().toISOString()
            }));
            console.log('💾 Rascunho salvo automaticamente');
        } catch (error) {
            console.error('Erro ao salvar rascunho:', error);
        }
    },
    
    /**
     * Carregar rascunho
     */
    loadDraft() {
        try {
            const draft = localStorage.getItem(`skeleton_draft_${this.config.skeletonId}`);
            if (draft) {
                const draftData = JSON.parse(draft);
                const draftTime = new Date(draftData.timestamp);
                const timeDiff = (new Date() - draftTime) / 1000 / 60; // minutos
                
                if (timeDiff < 60) { // Menos de 1 hora
                    if (confirm(`📝 Encontrado um rascunho salvo há ${Math.round(timeDiff)} minutos.\n\nDeseja restaurar as alterações?`)) {
                        this.data = draftData.data;
                        this.rebuildSectionsUI();
                        this.config.hasChanges = true;
                        this.showAlert('info', '📝 Rascunho restaurado! Lembre-se de salvar as alterações.');
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao carregar rascunho:', error);
        }
    },
    
    /**
     * Limpar rascunho
     */
    clearDraft() {
        try {
            localStorage.removeItem(`skeleton_draft_${this.config.skeletonId}`);
        } catch (error) {
            console.error('Erro ao limpar rascunho:', error);
        }
    },
    
    /**
     * Mostrar loading
     */
    showLoading(message = 'Processando...') {
        const overlay = document.getElementById('loadingOverlay');
        const content = overlay.querySelector('.loading-content p');
        if (content) content.textContent = message;
        overlay.style.display = 'flex';
    },
    
    /**
     * Ocultar loading
     */
    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    },
    
    /**
     * Mostrar alerta
     */
    showAlert(type, message, duration = 8000) {
        // Remove existing alerts (exceto o botão de salvar)
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => {
            if (alert.classList.contains('alert-dismissible') && !alert.closest('#saveChangesFooter')) {
                alert.remove();
            }
        });
        
        const iconMap = {
            'success': 'fas fa-check-circle',
            'danger': 'fas fa-exclamation-triangle',
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${iconMap[type] || 'fas fa-bell'} me-2"></i>
                <div class="flex-grow-1">${message}</div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        const flashMessages = container.querySelector('.flash-messages');
        
        if (flashMessages) {
            flashMessages.appendChild(alertDiv);
        } else {
            const flashDiv = document.createElement('div');
            flashDiv.className = 'flash-messages';
            flashDiv.appendChild(alertDiv);
            container.insertBefore(flashDiv, container.firstChild);
        }
        
        // Auto-remover
        if (duration > 0) {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, duration);
        }
        
        // Scroll para o topo
        //window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};

// Funções globais para compatibilidade com onclick inline
function toggleEditMode() {
    SkeletonEditor.toggleEditMode();
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

function editUrgencyElements() {
    SkeletonEditor.editUrgencyElements();
}

function editSecondaryGoals() {
    SkeletonEditor.editSecondaryGoals();
}

function addNewSection() {
    SkeletonEditor.addNewSection();
}

function saveNewSection() {
    SkeletonEditor.saveNewSection();
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

// Exportar para uso global
window.SkeletonEditor = SkeletonEditor;

// Log de inicialização
console.log('🎨 Skeleton Editor carregado!');
console.log('⌨️ Atalhos disponíveis:');
console.log('  - Ctrl/Cmd + E: Alternar modo de edição');
console.log('  - Ctrl/Cmd + S: Salvar alterações');
console.log('  - Escape: Sair do modo de edição');
