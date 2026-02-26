"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { HardDrive, UploadCloud, FileType, CheckCircle, Loader2 } from "lucide-react";

interface MLModel {
  id: number;
  filename: string;
  description: string;
  framework: string;
  is_active: boolean;
  upload_date: string;
}

export default function ModelsPage() {
  const [models, setModels] = useState<MLModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  
  // Upload Form
  const [file, setFile] = useState<File | null>(null);
  const [desc, setDesc] = useState("");
  const [framework, setFramework] = useState("yolo");

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const res = await api.get("/models");
      setModels(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("description", desc);
      formData.append("framework", framework);
      formData.append("set_active", "true"); // Ativar imediatamente ao subir

      await api.post("/models/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });
      
      setShowModal(false);
      setFile(null);
      setDesc("");
      fetchModels();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erro no upload. Arquivo não suportado.");
    } finally {
      setUploading(false);
    }
  };

  const setAsActive = async (id: number) => {
    try {
      setLoading(true);
      await api.put(`/models/${id}/activate`);
      fetchModels();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white dark:bg-zinc-900 p-6 rounded-2xl border border-gray-100 dark:border-zinc-800 shadow-sm animate-in fade-in slide-in-from-top-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white flex items-center gap-3">
             Hub de Modelos <span className="px-2 py-0.5 rounded-md bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 text-xs font-bold uppercase">MLOps</span>
          </h1>
          <p className="text-gray-500 text-sm mt-1">Gerencie os pesos treinados e frameworks (YOLO ou MediaPipe).</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium transition-colors shadow-blue-600/20 shadow-lg"
        >
          <UploadCloud size={18} /> Importar Pesos
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-8 duration-500">
        {loading && models.length === 0 ? (
          <div className="col-span-full py-12 flex justify-center">
             <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : models.map((m) => (
          <div 
            key={m.id} 
            className={`bg-white dark:bg-zinc-900 p-6 rounded-2xl border shadow-sm transition-all duration-300 relative overflow-hidden group hover:-translate-y-1 hover:shadow-xl ${
              m.is_active 
                ? "border-emerald-500/50 shadow-emerald-500/10" 
                : "border-gray-100 dark:border-zinc-800"
            }`}
          >
            {m.is_active && (
              <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-emerald-400 to-emerald-500" />
            )}
            
            <div className="flex justify-between items-start mb-4">
              <div className={`p-3 rounded-xl ${
                m.framework === 'yolo' ? 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400' 
                : 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400'
              }`}>
                <HardDrive size={24} />
              </div>

              {m.is_active ? (
                <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-widest bg-emerald-50 dark:bg-emerald-950/40 px-3 py-1.5 rounded-full">
                  <CheckCircle size={14} /> Em Uso
                </span>
              ) : (
                <button 
                  onClick={() => setAsActive(m.id)}
                  className="text-xs font-medium text-gray-500 dark:text-zinc-400 hover:text-blue-600 dark:hover:text-blue-400 border border-gray-200 dark:border-zinc-700 hover:border-blue-200 px-3 py-1.5 rounded-full transition-colors opacity-0 group-hover:opacity-100"
                >
                  Tornar Ativo
                </button>
              )}
            </div>

            <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate" title={m.filename}>
              {m.filename}
            </h3>
            <p className="text-sm text-gray-500 dark:text-zinc-400 mt-1 line-clamp-2 h-10">
              {m.description || "Nenhuma descrição informada."}
            </p>

            <div className="flex items-center gap-4 mt-6 pt-4 border-t border-gray-100 dark:border-zinc-800 text-xs">
               <div className="flex items-center gap-1.5 text-gray-500 dark:text-zinc-400 font-medium">
                  <FileType size={14} /> Framework: <span className="uppercase text-gray-900 dark:text-zinc-300 ml-1">{m.framework}</span>
               </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-zinc-900 rounded-2xl w-full max-w-lg p-6 shadow-2xl border border-gray-100 dark:border-zinc-800 animate-in zoom-in-95 duration-200">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <UploadCloud className="text-blue-500" />
              Importar Modelo
            </h2>
            <form onSubmit={handleUpload} className="space-y-4">
              
              <div className="border-2 border-dashed border-gray-300 dark:border-zinc-700 rounded-xl p-8 text-center hover:bg-gray-50 dark:hover:bg-zinc-800/50 transition-colors cursor-pointer relative">
                <input 
                  type="file" 
                  accept=".pt,.pkl,.onnx,.h5"
                  required
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="text-gray-500 dark:text-zinc-400 font-medium cursor-pointer flex flex-col items-center">
                   {file ? (
                     <>
                      <File size={32} className="text-blue-500 mb-2" />
                      <span className="text-gray-900 dark:text-zinc-200">{file.name}</span>
                     </>
                   ) : (
                     <>
                      <UploadCloud size={32} className="text-gray-400 mb-2" />
                      <span>Arraste o arquivo .pt ou .pkl aqui</span>
                      <span className="text-xs mt-2 text-gray-400">Até 500MB nativo no FastAPI via FileStream</span>
                     </>
                   )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Framework de Visão</label>
                <select 
                  value={framework} 
                  onChange={e => setFramework(e.target.value)}
                  className="w-full border border-gray-200 dark:border-zinc-700 rounded-xl px-4 py-3 bg-white dark:bg-zinc-800 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="yolo">YOLOv8 Pose Estimation (Ultralytics)</option>
                  <option value="mediapipe">MediaPipe Heuristics</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Anotações / Descrição do Dataset</label>
                <textarea 
                  value={desc} 
                  onChange={e => setDesc(e.target.value)}
                  placeholder="Ex: Treinado com o MPII Human Pose Dataset por 50 epochs..."
                  className="w-full border border-gray-200 dark:border-zinc-700 rounded-xl px-4 py-3 bg-white dark:bg-zinc-800 dark:text-white focus:ring-2 focus:ring-blue-500 resize-none h-24" 
                />
              </div>

              <div className="flex gap-3 justify-end mt-8 pt-4 border-t border-gray-100 dark:border-zinc-800">
                <button 
                  type="button" 
                  disabled={uploading}
                  onClick={() => setShowModal(false)} 
                  className="px-5 py-2.5 rounded-xl text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-zinc-800 transition-colors font-medium"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  disabled={uploading || !file}
                  className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium transition-colors"
                >
                  {uploading ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Transferindo...</>
                  ) : "Iniciar Upload"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
