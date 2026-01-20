<template>
  <div class="admin-layout">
    
    <div class="page-header">
      <div class="header-content">
        <button class="btn-back" @click="$router.push('/admin/dashboard')">
          <span class="icon">←</span> Volver
        </button>
        <h2>Nuevo Restaurante</h2>
      </div>
    </div>

    <div class="form-container">
      <div class="card form-card">
        
        <form @submit.prevent="submitRestaurant">
          
          <div class="section-title">
            <span class="step-number">1</span>
            <h3>Asignar Propietario</h3>
          </div>
          
          <div class="form-group owner-select-group">
            <label>Selecciona el Dueño</label>
            <div class="select-wrapper">
              <select v-model="form.id_dueno" required :disabled="loadingOwners || availableOwners.length === 0">
                <option value="" disabled selected>-- Elige un usuario --</option>
                <option v-for="owner in availableOwners" :key="owner.id" :value="owner.id">
                  👤 {{ owner.name }} ({{ owner.email }})
                </option>
              </select>
              <div class="select-arrow">▼</div>
            </div>

            <div v-if="availableOwners.length === 0 && !loadingOwners" class="alert-box warning">
              <div class="alert-icon">⚠️</div>
              <div class="alert-content">
                <strong>No hay dueños disponibles.</strong>
                <p>Todos los usuarios con rol 'Dueño' ya tienen un restaurante asignado o no existen.</p>
                <button type="button" @click="$router.push('/admin/dashboard')" class="btn-link">Gestionar Usuarios</button>
              </div>
            </div>
          </div>

          <div class="section-divider"></div>
          <div class="section-title">
            <span class="step-number">2</span>
            <h3>Identidad del Restaurante</h3>
          </div>

          <div class="split-layout">
            <div class="left-col">
              <div class="form-group">
                <label>Nombre del Restaurante</label>
                <input v-model="form.nombre" type="text" placeholder="Ej. La Casa del Sabor" required />
              </div>
              
              <div class="form-group">
                <label>Dirección</label>
                <input v-model="form.direccion" type="text" placeholder="Calle Principal #123" required />
              </div>

              <div class="form-group">
                <label>Teléfono de Contacto</label>
                <input v-model="form.telefono" type="tel" placeholder="099 123 4567" required />
              </div>
            </div>

            <div class="right-col">
              <label>Logotipo</label>
              <div 
                class="upload-area" 
                :class="{ 'has-image': logoPreview }"
                @click="triggerFileInput"
              >
                <input 
                  type="file" 
                  ref="fileInput" 
                  @change="handleFileUpload" 
                  accept="image/*" 
                  hidden 
                />
                
                <div v-if="logoPreview" class="preview-container">
                  <img :src="logoPreview" alt="Logo Preview" />
                  <div class="overlay">
                    <span>Cambiar imagen</span>
                  </div>
                </div>

                <div v-else class="placeholder">
                  <span class="upload-icon">☁️</span>
                  <p>Click para subir logo</p>
                  <small>JPG o PNG</small>
                </div>
              </div>
            </div>
          </div>

          <div class="section-divider"></div>
          <div class="section-title">
            <span class="step-number">3</span>
            <h3>Horario de Atención</h3>
          </div>

          <div class="time-grid">
            <div class="time-input">
              <label>Apertura ☀️</label>
              <input v-model="form.horario_apertura" type="time" required />
            </div>
            <div class="separator">a</div>
            <div class="time-input">
              <label>Cierre 🌙</label>
              <input v-model="form.horario_cierre" type="time" required />
            </div>
          </div>

          <div class="form-actions">
            <p v-if="errorMessage" class="msg error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="msg success">{{ successMessage }}</p>
            
            <button type="submit" class="btn-submit" :disabled="loading || (availableOwners.length === 0)">
              <span v-if="loading" class="spinner"></span>
              {{ loading ? 'Creando...' : '✨ Registrar Restaurante' }}
            </button>
          </div>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const loadingOwners = ref(true);
const availableOwners = ref([]);
const errorMessage = ref('');
const successMessage = ref('');
const logoFile = ref(null);
const logoPreview = ref(null);
const fileInput = ref(null);

// MODIFICADO: Usamos id_dueno en lugar de email_dueno
const form = ref({
  nombre: '',
  id_dueno: '', 
  direccion: '',
  telefono: '',
  horario_apertura: '08:00',
  horario_cierre: '22:00'
});

onMounted(async () => {
    try {
        const res = await axios.get('/api/users/available-owners');
        availableOwners.value = res.data;
    } catch (error) {
        console.error("Error cargando dueños:", error);
    } finally {
        loadingOwners.value = false;
    }
});

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      logoFile.value = file;
      logoPreview.value = URL.createObjectURL(file);
    }
};

const submitRestaurant = async () => {
  loading.value = true;
  errorMessage.value = '';

  try {
    const formData = new FormData();
    formData.append('nombre', form.value.nombre);
    // MODIFICADO: Enviamos id_dueno
    formData.append('id_dueno', form.value.id_dueno);
    formData.append('direccion', form.value.direccion);
    formData.append('telefono', form.value.telefono);
    formData.append('horario_apertura', form.value.horario_apertura);
    formData.append('horario_cierre', form.value.horario_cierre);
    
    if (logoFile.value) {
        formData.append('logo', logoFile.value);
    }

    await axios.post('/api/admin/restaurants/create', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });

    successMessage.value = '¡Restaurante creado con éxito!';
    setTimeout(() => router.push('/admin/dashboard'), 1500);

  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Error al crear restaurante';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* VARIABLES */
:root {
  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --bg-color: #f3f4f6;
  --text-main: #1f2937;
  --text-light: #6b7280;
}

.admin-layout {
  background-color: var(--bg-color, #f3f4f6);
  min-height: 100vh;
  padding-bottom: 40px;
  font-family: 'Segoe UI', sans-serif;
}

/* HEADER */
.page-header {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-content h2 { margin: 0; color: #111827; font-size: 1.5rem; }

.btn-back {
  background: none; border: none; color: #6b7280; 
  cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 5px;
  transition: color 0.2s;
}
.btn-back:hover { color: #111827; }

/* CARD */
.form-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

.form-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.04);
  padding: 2.5rem;
}

/* SECTIONS */
.section-title {
  display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;
}
.step-number {
  background: #e0e7ff; color: #4f46e5; width: 28px; height: 28px;
  border-radius: 50%; display: flex; justify-content: center; align-items: center;
  font-weight: bold; font-size: 0.9rem;
}
.section-title h3 { margin: 0; font-size: 1.1rem; color: #374151; }

.section-divider {
  height: 1px; background: #f3f4f6; margin: 2rem 0;
}

/* INPUTS */
.form-group { margin-bottom: 1.2rem; }
label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #374151; font-size: 0.9rem; }

input[type="text"], input[type="tel"], select, input[type="time"] {
  width: 100%; padding: 12px 16px; border: 1px solid #e5e7eb; border-radius: 8px;
  font-size: 0.95rem; transition: all 0.2s; background: #f9fafb;
}

input:focus, select:focus {
  border-color: #4f46e5; background: white; outline: none; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* SELECT */
.select-wrapper { position: relative; }
.select-arrow {
  position: absolute; right: 15px; top: 50%; transform: translateY(-50%);
  color: #6b7280; pointer-events: none; font-size: 0.8rem;
}
select { appearance: none; cursor: pointer; }

/* ALERT */
.alert-box {
  background: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px;
  padding: 1rem; margin-top: 10px; display: flex; gap: 12px;
}
.alert-icon { font-size: 1.5rem; }
.alert-content p { margin: 4px 0; font-size: 0.9rem; color: #92400e; }
.btn-link { 
  background: none; border: none; color: #b45309; text-decoration: underline; 
  cursor: pointer; padding: 0; font-weight: 600;
}

/* UPLOAD & LAYOUT */
.split-layout { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; }

.upload-area {
  border: 2px dashed #e5e7eb; border-radius: 12px; height: 100%; min-height: 200px;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  cursor: pointer; transition: all 0.3s; background: #f9fafb; position: relative; overflow: hidden;
}
.upload-area:hover { border-color: #4f46e5; background: #eff6ff; }

.placeholder { text-align: center; color: #6b7280; }
.upload-icon { font-size: 2.5rem; display: block; margin-bottom: 10px; }

.preview-container { width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
.preview-container img { width: 100%; height: 100%; object-fit: cover; }
.overlay {
  position: absolute; bottom: 0; width: 100%; background: rgba(0,0,0,0.6);
  color: white; text-align: center; padding: 8px; font-size: 0.85rem;
  opacity: 0; transition: opacity 0.2s;
}
.upload-area:hover .overlay { opacity: 1; }

/* TIME GRID */
.time-grid { display: flex; align-items: flex-end; gap: 1rem; max-width: 400px; }
.time-input { flex: 1; }
.separator { padding-bottom: 12px; color: #9ca3af; font-weight: bold; }

/* ACTIONS */
.form-actions { margin-top: 2rem; }
.btn-submit {
  width: 100%; background: linear-gradient(135deg, #4f46e5, #4338ca);
  color: white; border: none; padding: 14px; border-radius: 10px;
  font-size: 1rem; font-weight: 600; cursor: pointer; transition: transform 0.2s;
  display: flex; justify-content: center; align-items: center; gap: 10px;
}
.btn-submit:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }
.btn-submit:disabled { background: #9ca3af; cursor: not-allowed; }

.msg { text-align: center; font-weight: 600; margin-bottom: 1rem; }
.error { color: #ef4444; }
.success { color: #10b981; }

@media (max-width: 768px) {
  .split-layout { grid-template-columns: 1fr; }
  .upload-area { min-height: 150px; margin-top: 1rem; }
}
</style>