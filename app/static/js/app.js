/* EDUFACE - JavaScript principal - v2.1 */

// Variables globales
let stream, timer, running = false, busy = false;
let ch1, ch2, ch3, ch4; // Charts

// Inicialización cuando carga la página
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

function initializeApp() {
    // Configurar fecha actual en el exportador (fecha local)
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const todayString = `${year}-${month}-${day}`;
    
    const exportDateField = document.getElementById('exportDate');
    if (exportDateField) {
        exportDateField.value = todayString;
    }
    
    // Cargar opciones de grado y sección para los filtros
    loadGradeOptions();
}

function setupEventListeners() {
    // Gestión de pestañas
    document.querySelectorAll('.tab').forEach(tab => {
        tab.onclick = () => switchTab(tab);
    });

    // Controles de cámara
    document.getElementById('btnStart').onclick = startFaceRecognition;
    document.getElementById('btnStop').onclick = stopFaceRecognition;

    // Filtros y actualizaciones
    document.getElementById('btnRefresh').onclick = refreshReports;
    document.getElementById('btnExportPDF').onclick = exportToPDF;

    // Gestión de estudiantes
    document.getElementById('btnAddStudent').onclick = showAddStudentModal;

    // Cerrar modal con Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });
}

function loadInitialData() {
    // Cargar datos de la pestaña activa (tiempo real)
    refreshToday();
    refreshTodayKPIs();
}

// === MODAL ESTUDIANTE ===
async function showStudentProfile(studentId) {
    try {
        console.log('Cargando perfil del estudiante ID:', studentId);
        
        // Cargar datos del estudiante
        const studentResponse = await fetch(`/students/${studentId}`);
        if (!studentResponse.ok) {
            throw new Error(`Error al cargar estudiante: ${studentResponse.status}`);
        }
        const student = await studentResponse.json();
        
        // Cargar historial de asistencia
        const attendanceResponse = await fetch(`/students/${studentId}/attendance?limit=20`);
        if (!attendanceResponse.ok) {
            throw new Error(`Error al cargar historial: ${attendanceResponse.status}`);
        }
        const attendance = await attendanceResponse.json();
        
        // Calcular estadísticas
        const totalDays = attendance.length;
        const punctualDays = attendance.filter(a => a.status === 'Puntual').length;
        const lateDays = attendance.filter(a => a.status === 'Tarde' || a.status === 'Muy Tarde').length;
        const punctualPercentage = totalDays > 0 ? Math.round((punctualDays / totalDays) * 100) : 0;
        
        // Foto del estudiante
        const photoImg = student.photo_path ? 
            `<img src="${student.photo_path}" alt="Foto de ${student.name}" style="width:80px;height:80px;object-fit:cover;border-radius:50%;margin-bottom:15px;"/>` : 
            '<div style="width:80px;height:80px;background:#f0f0f0;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:15px;font-size:30px;">👤</div>';
        
        // HTML del modal
        const modalHTML = `
            <div style="text-align:center;margin-bottom:20px;">
                ${photoImg}
                <h3 style="margin:0 0 5px 0;color:#2d3748;">${student.name}</h3>
                <div style="color:#718096;font-size:14px;margin-bottom:15px;">
                    Código: ${student.code} ${student.grade ? `• ${student.grade}` : ''} ${student.section ? student.section : ''}
                </div>
                
                <!-- Estadísticas rápidas -->
                <div style="display:flex;justify-content:space-around;margin-bottom:20px;background:#f7fafc;padding:15px;border-radius:10px;">
                    <div style="text-align:center;">
                        <div style="font-size:20px;font-weight:bold;color:#38a169;">${punctualDays}</div>
                        <div style="font-size:12px;color:#718096;">Puntual</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:20px;font-weight:bold;color:#ed8936;">${lateDays}</div>
                        <div style="font-size:12px;color:#718096;">Tarde</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:20px;font-weight:bold;color:#3182ce;">${punctualPercentage}%</div>
                        <div style="font-size:12px;color:#718096;">Puntualidad</div>
                    </div>
                </div>
            </div>
            
            <h4 style="margin:20px 0 10px 0;color:#2d3748;">📅 Historial de Asistencia (últimos 20 días)</h4>
            <div style="max-height:300px;overflow-y:auto;">
                ${attendance.length === 0 ? 
                    '<p style="text-align:center;color:#718096;padding:20px;">No hay registros de asistencia</p>' :
                    attendance.map(record => {
                        const statusPill = createStatusPill(record.status);
                        
                        // Crear fecha desde los campos date y time del backend
                        const dateTime = `${record.date}T${record.time}`;
                        const date = new Date(dateTime);
                        
                        const dateStr = date.toLocaleDateString('es-ES', { 
                            weekday: 'short', 
                            year: 'numeric', 
                            month: 'short', 
                            day: 'numeric' 
                        });
                        const timeStr = date.toLocaleTimeString('es-ES', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                        });
                        
                        return `
                            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #e2e8f0;">
                                <div>
                                    <div style="font-weight:600;color:#2d3748;">${dateStr}</div>
                                    <div style="font-size:13px;color:#718096;">${timeStr}</div>
                                </div>
                                ${statusPill}
                            </div>
                        `;
                    }).join('')
                }
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding: 0 20px;">
                <button onclick="closeModal()" class="btn-modal-close">
                    🚪 Cerrar
                </button>
            </div>
        `;
        
        openModal(modalHTML);
        
    } catch (error) {
        console.error('Error al cargar perfil del estudiante:', error);
        showToast(`Error al cargar el perfil del estudiante: ${error.message}`, 'error');
    }
}

// === MODAL ESTUDIANTE ===
function switchTab(activeTab) {
    // Actualizar estados visuales
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    activeTab.classList.add('active');
    
    const tabKey = activeTab.dataset.tab;
    
    // Mostrar/ocultar secciones
    ['realtime', 'reports', 'analysis', 'manage'].forEach(id => {
        document.getElementById(id).style.display = (id === tabKey) ? 'block' : 'none';
    });
    
    // Cargar contenido específico de cada pestaña
    switch(tabKey) {
        case 'realtime':
            refreshToday();
            refreshTodayKPIs();
            break;
        case 'reports':
            loadSummary();
            loadWeekly();
            loadByGrade();
            break;
        case 'analysis':
            loadDetailed();
            break;
        case 'manage':
            loadStudents();
            break;
    }
}

// === RECONOCIMIENTO FACIAL ===
async function startFaceRecognition() {
    if (running) return;
    
    try {
        // Iniciar cámara
        stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 }
        });
        
        const videoElement = document.getElementById('cam');
        videoElement.srcObject = stream;
        
        // Ocultar overlay y mostrar controles
        document.getElementById('camOverlay').style.display = 'none';
        document.getElementById('stopRow').style.display = 'flex';
        document.getElementById('statusIndicator').style.display = 'flex';
        document.getElementById('statusText').textContent = '🔍 Sistema activado - Esperando rostros...';
        
        running = true;
        
        // Iniciar loop de reconocimiento
        recognitionLoop();
        
        showToast('Sistema de reconocimiento iniciado', 'success');
        
    } catch (error) {
        console.error('Error al iniciar cámara:', error);
        showToast('Error al acceder a la cámara', 'error');
    }
}

function stopFaceRecognition() {
    running = false;
    
    // Detener timer
    if (timer) {
        clearTimeout(timer);
        timer = null;
    }
    
    // Detener stream de video
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    // Resetear UI
    const videoElement = document.getElementById('cam');
    videoElement.srcObject = null;
    document.getElementById('camOverlay').style.display = 'flex';
    document.getElementById('stopRow').style.display = 'none';
    document.getElementById('statusIndicator').style.display = 'none';
    
    showToast('Sistema de reconocimiento detenido', 'info');
}

async function recognitionLoop() {
    if (!running) return;
    
    // Evitar solapamiento de capturas
    if (busy) {
        timer = setTimeout(recognitionLoop, 200); // Retry más rápido si está ocupado
        return;
    }
    
    busy = true;
    
    try {
        await captureAndRecognize();
    } catch (error) {
        console.error('Error en reconocimiento:', error);
    } finally {
        busy = false;
    }
    
    // Programar siguiente captura (cada 2 segundos para mayor responsividad)
    timer = setTimeout(recognitionLoop, 2000);
}

async function captureAndRecognize() {
    const videoElement = document.getElementById('cam');
    const canvas = document.createElement('canvas');
    
    // Actualizar indicador de estado
    document.getElementById('statusText').textContent = '🔍 Analizando rostro detectado...';
    
    // Mostrar indicador de procesamiento
    showToast('🔍 Procesando reconocimiento...', 'info', 1000);
    
    // Configurar canvas con resolución apropiada
    const width = 360;
    const height = Math.round(360 / (videoElement.videoWidth / videoElement.videoHeight));
    
    canvas.width = width;
    canvas.height = height;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0, width, height);
    
    // Convertir a blob con mayor calidad
    const blob = await new Promise(resolve => 
        canvas.toBlob(resolve, 'image/jpeg', 0.95)  // Aumentar calidad a 95%
    );
    
    // Enviar al servidor
    const formData = new FormData();
    formData.append('img', blob, 'frame.jpg');
    formData.append('db_path', 'db');
    
    try {
        const response = await fetch('/attendance/mark', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Resultado del reconocimiento:', result);  // Debug
            
            if (result.status === 'success') {
                // Mostrar mensaje de BIENVENIDA la primera vez
                const message = `🎉 ¡Bienvenido ${result.student_name}! Asistencia registrada exitosamente`;
                showToast(message, 'success', 4000);
                
                // Actualizar indicador de estado
                document.getElementById('statusText').textContent = `✅ ${result.student_name} registrado correctamente`;
                
                // Actualizar listas en tiempo real INMEDIATAMENTE
                await refreshToday();
                await refreshTodayKPIs();
                
            } else if (result.status === 'already_marked') {
                const message = `⚠️ ${result.student_name} ya registró asistencia a las ${result.existing_time}`;
                showToast(message, 'warning', 4000);
                
                // Actualizar indicador de estado
                document.getElementById('statusText').textContent = `⚠️ ${result.student_name} ya fue registrado`;
                
            } else if (result.status === 'unknown') {
                showToast(`❌ Persona no reconocida. Motivo: ${result.reason}`, 'error', 3000);
                console.log('Detalles del error:', result);
                
                // Actualizar indicador de estado
                document.getElementById('statusText').textContent = '❌ Rostro no reconocido';
            }
            
            // Restaurar indicador después de 3 segundos
            setTimeout(() => {
                if (running) {
                    document.getElementById('statusText').textContent = '🔍 Sistema activado - Esperando rostros...';
                }
            }, 3000);
            
        } else {
            const errorText = await response.text();
            console.error('Error del servidor:', errorText);
            showToast('🔥 Error del servidor', 'error', 3000);
        }
    } catch (error) {
        console.error('Error al enviar imagen:', error);
    } finally {
        // Restaurar estado del indicador
        document.getElementById('statusText').textContent = '🔍 Sistema activado - Esperando rostros...';
    }
}

// === GESTIÓN DE DATOS ===
async function refreshToday() {
    try {
        const response = await fetch('/attendance/today');
        const attendanceList = await response.json();
        
        const container = document.getElementById('recentList');
        container.innerHTML = attendanceList.map(item => {
            const gradeSection = (item.grade || '') + (item.section ? (' ' + item.section) : '');
            const statusPill = createStatusPill(item.status);
            
            return `
                <div class="cardItem" style="border:1px solid #e5e5e5;border-radius:10px;padding:12px;margin:8px 0;cursor:pointer;" onclick="showStudentProfile(${item.student_id})">
                    <div style="font-weight:700;margin-bottom:4px;">${item.student_name}</div>
                    <div style="font-size:13px;color:#555;margin-bottom:2px;">Código: ${item.student_code}</div>
                    <div style="font-size:13px;color:#555;margin-bottom:6px;">
                        ${gradeSection} • ${item.time}
                    </div>
                    ${statusPill}
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error al cargar asistencia de hoy:', error);
    }
}

async function refreshTodayKPIs() {
    try {
        const response = await fetch('/attendance/metrics/today');
        const metrics = await response.json();
        
        document.getElementById('k_today').textContent = metrics.total_today || 0;
        document.getElementById('k_punctual_today').textContent = metrics.punctual_today || 0;
        document.getElementById('k_late_today').textContent = metrics.late_today || 0;
        document.getElementById('k_absent_today').textContent = metrics.absent_today || 0;
        
    } catch (error) {
        console.error('Error al cargar métricas:', error);
    }
}

async function loadSummary() {
    try {
        const period = document.getElementById('period').value;
        const grade = document.getElementById('grade').value;
        const section = document.getElementById('section').value;
        
        const params = new URLSearchParams();
        if (period) params.append('period', period);
        if (grade) params.append('grade', grade);
        if (section) params.append('section', section);
        
        const response = await fetch(`/reports/summary?${params.toString()}`);
        const data = await response.json();
        
        document.getElementById('k_students').textContent = data.students_total || 0;
        document.getElementById('k_records').textContent = data.records_total || 0;
        document.getElementById('k_punctual').textContent = (data.punctuality_pct || 0) + '%';
        document.getElementById('k_late').textContent = (data.late_pct || 0) + '%';
        document.getElementById('k_absent').textContent = (data.absent_pct || 0) + '%';
        
    } catch (error) {
        console.error('Error al cargar resumen:', error);
    }
}

async function loadWeekly() {
    try {
        const response = await fetch('/attendance/metrics/weekly');
        const data = await response.json();
        
        const ctx = document.getElementById('chWeekly').getContext('2d');
        
        if (ch1) ch1.destroy();
        
        ch1 = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Asistencia %',
                    data: data.attendance_pct || [],
                    fill: true,
                    borderColor: '#3f51b5',
                    backgroundColor: 'rgba(63,81,181,.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error al cargar gráfico semanal:', error);
    }
}

async function loadByGrade() {
    try {
        const response = await fetch('/attendance/metrics/by-grade');
        const data = await response.json();
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        const ctx = document.getElementById('chGrade').getContext('2d');
        
        if (ch2) ch2.destroy();
        
        ch2 = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Asistencia (hoy)',
                    data: values,
                    backgroundColor: '#7ea1ff',
                    borderColor: '#5a7fff',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error al cargar gráfico por grado:', error);
    }
}

async function loadDetailed() {
    try {
        const response = await fetch('/reports/detailed');
        const data = await response.json();
        
        // Gráfico de distribución por género
        if (data.gender_distribution) {
            const genderLabels = Object.keys(data.gender_distribution);
            const genderData = Object.values(data.gender_distribution);
            
            const genderCtx = document.getElementById('chGender').getContext('2d');
            
            if (ch3) ch3.destroy();
            
            ch3 = new Chart(genderCtx, {
                type: 'doughnut',
                data: {
                    labels: genderLabels,
                    datasets: [{
                        data: genderData,
                        backgroundColor: ['#80cbc4', '#64b5f6', '#ffe082', '#e57373']
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }
        
        // Gráfico de patrones de llegada
        if (data.arrival_buckets) {
            const arrivalLabels = Object.keys(data.arrival_buckets);
            const arrivalData = Object.values(data.arrival_buckets);
            
            const arrivalCtx = document.getElementById('chArrival').getContext('2d');
            
            if (ch4) ch4.destroy();
            
            ch4 = new Chart(arrivalCtx, {
                type: 'bar',
                data: {
                    labels: arrivalLabels,
                    datasets: [{
                        label: 'Cantidad de estudiantes',
                        data: arrivalData,
                        backgroundColor: '#9ccc65'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Cargar tabla de registros recientes
        await loadRecentTable();
        
    } catch (error) {
        console.error('Error al cargar análisis detallado:', error);
    }
}

async function loadRecentTable() {
    try {
        const response = await fetch('/attendance/recent?limit=10');
        const records = await response.json();
        
        const tableBody = document.getElementById('tblRecent');
        tableBody.innerHTML = records.map(record => `
            <tr>
                <td>${record.student_name}</td>
                <td>${(record.grade || '') + ' ' + (record.section || '')}</td>
                <td>${record.date}</td>
                <td>${record.time}</td>
                <td>${createStatusPill(record.status)}</td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error al cargar tabla reciente:', error);
    }
}

async function loadStudents() {
    try {
        const response = await fetch('/students');
        const students = await response.json();
        
        const tableBody = document.getElementById('tblStudents');
        tableBody.innerHTML = students.map(student => {
            const photoImg = student.photo_path ? 
                `<img src="${student.photo_path}" alt="foto" style="width:40px;height:40px;object-fit:cover;border-radius:6px;"/>` : 
                '<span style="color:#999;">Sin foto</span>';
                
            return `
                <tr style="cursor:pointer;" data-student-id="${student.id}">
                    <td>${student.name}</td>
                    <td>${student.grade || '-'}</td>
                    <td>${student.section || '-'}</td>
                    <td>${student.gender || '-'}</td>
                    <td>${formatDate(student.registration_date) || '-'}</td>
                    <td>${photoImg}</td>
                    <td style="text-align:center;">
                        <button class="btn-edit" data-student-id="${student.id}">✏️ Editar</button>
                        <button class="btn-delete" data-student-id="${student.id}">🗑️ Eliminar</button>
                    </td>
                </tr>
            `;
        }).join('');
        
        // Configurar event delegation
        setupStudentTableEvents();
        
    } catch (error) {
        console.error('Error al cargar estudiantes:', error);
    }
}

function setupStudentTableEvents() {
    const tableBody = document.getElementById('tblStudents');
    
    // Remover listeners anteriores si existen
    tableBody.removeEventListener('click', handleTableClick);
    
    // Agregar nuevo listener
    tableBody.addEventListener('click', handleTableClick);
}

function handleTableClick(event) {
    const target = event.target;
    const row = target.closest('tr');
    
    if (!row) return;
    
    const studentId = row.getAttribute('data-student-id');
    
    if (target.classList.contains('btn-edit')) {
        event.stopPropagation();
        console.log('Edit button clicked for student:', studentId);
        editStudent(parseInt(studentId));
    } else if (target.classList.contains('btn-delete')) {
        event.stopPropagation();
        deleteStudent(parseInt(studentId));
    } else {
        // Click en la fila
        showStudentProfile(parseInt(studentId));
    }
}

// === GESTIÓN DE ESTUDIANTES ===
function showAddStudentModal() {
    const modalHTML = `
        <h3>➕ Agregar Nuevo Estudiante</h3>
        <form id="studentForm" enctype="multipart/form-data">
            <div class="form-row">
                <div class="form-group">
                    <label>Nombre Completo *</label>
                    <input type="text" name="name" required placeholder="Ej: Juan Pérez García"/>
                </div>
                <div class="form-group">
                    <label>Código de Estudiante *</label>
                    <input type="text" name="code" required placeholder="Ej: EST2024001"/>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Grado</label>
                    <select name="grade">
                        <option value="">Seleccionar grado</option>
                        <option value="1">1° Grado</option>
                        <option value="2">2° Grado</option>
                        <option value="3">3° Grado</option>
                        <option value="4">4° Grado</option>
                        <option value="5">5° Grado</option>
                        <option value="6">6° Grado</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Sección</label>
                    <select name="section">
                        <option value="">Seleccionar sección</option>
                        <option value="A">Sección A</option>
                        <option value="B">Sección B</option>
                        <option value="C">Sección C</option>
                        <option value="D">Sección D</option>
                    </select>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Género</label>
                    <select name="gender">
                        <option value="">Seleccionar género</option>
                        <option value="Femenino">Femenino</option>
                        <option value="Masculino">Masculino</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Fecha de Registro</label>
                    <input type="date" name="registration_date" value="${new Date().toISOString().split('T')[0]}"/>
                </div>
            </div>
            
            <div class="form-group">
                <label>Fotografía del Estudiante</label>
                <input type="file" name="photo" accept="image/*" id="photoInput"/>
                <div id="photoPreview" class="photoPreview mt-16">
                    <span>📷 Seleccionar foto</span>
                </div>
            </div>
            
            <div class="row mt-16">
                <button type="submit" class="btn-save">💾 Guardar Estudiante</button>
                <button type="button" onclick="closeModal()" class="btn-modal-cancel">❌ Cancelar</button>
            </div>
        </form>
    `;
    
    openModal(modalHTML);
    
    // Setup photo preview
    setupPhotoPreview();
    
    // Setup form submission
    document.getElementById('studentForm').addEventListener('submit', handleStudentSubmit);
}

function setupPhotoPreview() {
    const photoInput = document.getElementById('photoInput');
    const preview = document.getElementById('photoPreview');
    
    photoInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Vista previa"/>`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = '<span>📷 Seleccionar foto</span>';
        }
    });
}

async function handleStudentSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitButton = e.target.querySelector('button[type="submit"]');
    
    // Mostrar estado de carga
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '⏳ Guardando...';
    submitButton.disabled = true;
    
    try {
        const response = await fetch('/students/form', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            closeModal();
            showToast('Estudiante creado exitosamente', 'success');
            loadStudents(); // Recargar lista
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error al crear estudiante', 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
    } finally {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
}

async function editStudent(studentId) {
    console.log('editStudent called with ID:', studentId);
    try {
        // Obtener datos del estudiante
        const response = await fetch(`/students/${studentId}`);
        const student = await response.json();
        
        const modalHTML = `
            <form id="editStudentForm" enctype="multipart/form-data">
                <input type="hidden" name="student_id" value="${student.id}"/>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Nombre Completo *</label>
                        <input type="text" name="name" value="${student.name || ''}" required/>
                    </div>
                    <div class="form-group">
                        <label>Código de Estudiante *</label>
                        <input type="text" name="code" value="${student.code || ''}" required/>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Grado</label>
                        <select name="grade">
                            <option value="">Seleccionar grado</option>
                            ${[1,2,3,4,5,6].map(g => 
                                `<option value="${g}" ${student.grade == g ? 'selected' : ''}>${g}° Grado</option>`
                            ).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Sección</label>
                        <select name="section">
                            <option value="">Seleccionar sección</option>
                            ${['A','B','C','D'].map(s => 
                                `<option value="${s}" ${student.section === s ? 'selected' : ''}>Sección ${s}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Género</label>
                        <select name="gender">
                            <option value="">Seleccionar género</option>
                            <option value="Femenino" ${student.gender === 'Femenino' ? 'selected' : ''}>Femenino</option>
                            <option value="Masculino" ${student.gender === 'Masculino' ? 'selected' : ''}>Masculino</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Fecha de Registro</label>
                        <input type="date" name="registration_date" value="${student.registration_date || ''}"/>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Fotografía del Estudiante</label>
                    <input type="file" name="photo" accept="image/*" id="editPhotoInput"/>
                    <div id="editPhotoPreview" class="photoPreview mt-16">
                        ${student.photo_path ? 
                            `<img src="${student.photo_path}" alt="Foto actual"/>` : 
                            '<span>📷 Sin foto</span>'
                        }
                    </div>
                </div>
                
                <div class="row mt-16">
                    <button type="submit" class="btn-update">💾 Actualizar</button>
                    <button type="button" onclick="closeModal()" class="btn-modal-cancel">❌ Cancelar</button>
                </div>
            </form>
        `;
        
        const fullModalHTML = `
            <h3>✏️ Editar Estudiante</h3>
            ${modalHTML}
        `;
        
        openModal(fullModalHTML);
        
        // Dar tiempo al DOM para renderizar el modal antes de configurar event listeners
        setTimeout(() => {
            setupEditModalEvents();
        }, 100);
        
    } catch (error) {
        console.error('Error al cargar estudiante:', error);
        showToast('Error al cargar datos del estudiante', 'error');
    }
}

function setupEditModalEvents() {
    // Setup photo preview para edición
    const editPhotoInput = document.getElementById('editPhotoInput');
    const editPreview = document.getElementById('editPhotoPreview');
    
    if (editPhotoInput && editPreview) {
        editPhotoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    editPreview.innerHTML = `<img src="${e.target.result}" alt="Nueva foto"/>`;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Setup form submission para edición
    const editForm = document.getElementById('editStudentForm');
    if (editForm) {
        editForm.addEventListener('submit', handleEditSubmit);
    }
}

async function handleEditSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const studentId = formData.get('student_id');
    const submitButton = e.target.querySelector('button[type="submit"]');
    
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '⏳ Actualizando...';
    submitButton.disabled = true;
    
    try {
        const response = await fetch(`/students/${studentId}/form`, {
            method: 'PUT',
            body: formData
        });
        
        if (response.ok) {
            closeModal();
            showToast('Estudiante actualizado exitosamente', 'success');
            loadStudents();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error al actualizar estudiante', 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
    } finally {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
}

async function deleteStudent(studentId) {
    return new Promise((resolve) => {
        // Mostrar modal de confirmación
        const deleteModal = document.getElementById('deleteConfirmModal');
        const cancelBtn = document.getElementById('cancelDeleteBtn');
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        
        // Mostrar el modal
        deleteModal.style.display = 'flex';
        
        // Función para cerrar el modal
        const closeModal = () => {
            deleteModal.style.display = 'none';
            resolve(false);
        };
        
        // Función para confirmar eliminación
        const confirmDelete = async () => {
            deleteModal.style.display = 'none';
            
            try {
                const response = await fetch(`/students/${studentId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    showToast('Estudiante eliminado exitosamente', 'success');
                    loadStudents();
                } else {
                    showToast('Error al eliminar estudiante', 'error');
                }
                
            } catch (error) {
                console.error('Error:', error);
                showToast('Error de conexión', 'error');
            }
            
            resolve(true);
        };
        
        // Event listeners
        cancelBtn.onclick = closeModal;
        confirmBtn.onclick = confirmDelete;
        
        // Cerrar modal al hacer clic fuera de él
        deleteModal.onclick = (e) => {
            if (e.target === deleteModal) {
                closeModal();
            }
        };
        
        // Cerrar modal con tecla Escape
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    });
}

// === EXPORTACIÓN PDF ===
async function exportToPDF() {
    const date = document.getElementById('exportDate').value;
    const grade = document.getElementById('exportGrade').value;
    const section = document.getElementById('exportSection').value;
    const status = document.getElementById('exportStatus').value;
    
    if (!date) {
        showToast('Por favor selecciona una fecha', 'warning');
        return;
    }
    
    const params = new URLSearchParams();
    params.append('date', date);
    if (grade) params.append('grade', grade);
    if (section) params.append('section', section);
    if (status) params.append('status', status);
    
    const exportButton = document.getElementById('btnExportPDF');
    const originalText = exportButton.innerHTML;
    
    try {
        exportButton.innerHTML = '⏳ Generando PDF...';
        exportButton.disabled = true;
        
        const response = await fetch(`/reports/export/pdf?${params.toString()}`);
        
        if (!response.ok) {
            throw new Error('Error al generar PDF');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_asistencia_${date}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('PDF generado exitosamente', 'success');
        
    } catch (error) {
        console.error('Error al exportar PDF:', error);
        showToast('Error al generar PDF', 'error');
    } finally {
        exportButton.innerHTML = originalText;
        exportButton.disabled = false;
    }
}

// === UTILIDADES ===
function showToast(message, type = 'info', duration = 4000) {
    const toast = document.getElementById('toast');
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    const colors = {
        success: 'linear-gradient(135deg, #28a745, #20c997)',
        error: 'linear-gradient(135deg, #dc3545, #c82333)',
        warning: 'linear-gradient(135deg, #ffc107, #fd7e14)',
        info: 'linear-gradient(135deg, #4b3bc9, #6c56cf)'
    };
    
    toast.style.background = colors[type] || colors.info;
    toast.innerHTML = `<span>${icons[type] || icons.info}</span><span>${message}</span>`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

function createStatusPill(status) {
    const statusMap = {
        'Puntual': { class: 'status-puntual', icon: '✅', text: 'Puntual' },
        'Tarde': { class: 'status-tarde', icon: '⏰', text: 'Tarde' },
        'Muy Tarde': { class: 'status-tarde', icon: '⏰', text: 'Tarde' }, // Tratar "Muy Tarde" como "Tarde"
        'Ausente': { class: 'status-ausente', icon: '❌', text: 'Ausente' }
    };
    
    const statusInfo = statusMap[status] || { class: 'status-puntual', icon: '✅', text: status || 'Registrado' };
    
    return `<span class="status-pill ${statusInfo.class}">${statusInfo.icon} ${statusInfo.text}</span>`;
}

function formatDate(dateString) {
    if (!dateString) return '';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (error) {
        return dateString;
    }
}

function openModal(html) {
    document.getElementById('modalBody').innerHTML = html;
    document.getElementById('modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

function refreshReports() {
    loadSummary();
    loadWeekly();
    loadByGrade();
}

async function loadGradeOptions() {
    // Cargar opciones de grado para filtros de reportes
    const gradeSelects = ['grade', 'exportGrade'];
    
    gradeSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select && select.children.length <= 1) {
            for (let i = 1; i <= 6; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = `${i}°`;
                select.appendChild(option);
            }
        }
    });
}
