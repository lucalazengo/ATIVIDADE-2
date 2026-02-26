"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PlayCircle, UploadVideo, Video, Loader2, PieChart, Info, RefreshCw, BarChart } from "lucide-react";

interface PersonResult {
  person_id: string;
  time_standing_seconds: number;
  time_sitting_seconds: number;
  time_lying_seconds?: number;
  time_moving_seconds: number;
}

interface VideoAnalysis {
  id: number;
  video_id: string;
  status: string;
  analysis_timestamp: string;
  duration_seconds: number;
  people_detected: number;
  results: PersonResult[];
  error_message: string | null;
}

export default function VideosPage() {
  const [analyses, setAnalyses] = useState<VideoAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Upload states
  const [showUpload, setShowUpload] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchAnalyses();
    
    // Auto refresh while any status is 'processing'
    const interval = setInterval(() => {
      setAnalyses(curr => {
        if (curr.some(a => a.status === 'processing' || a.status === 'pending')) {
          fetchAnalyses(false);
        }
        return curr;
      });
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchAnalyses = async (showLoad = true) => {
    try {
      if (showLoad) setLoading(true);
      const res = await api.get("/videos");
      setAnalyses(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      if (showLoad) setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      await api.post("/videos/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      setShowUpload(false);
      setFile(null);
      fetchAnalyses();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erro no envio do vídeo.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white dark:bg-zinc-900 p-6 rounded-2xl border border-gray-100 dark:border-zinc-800 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white flex items-center gap-3">
             <Video className="text-blue-500" />
             Processamento em Lote
          </h1>
          <p className="text-gray-500 text-sm mt-1">Carregue vídeos (.mp4, .avi) do leito hospitalar para extração de telemetria.</p>
        </div>
        <button 
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-medium transition-all shadow-lg shadow-blue-600/20 active:scale-95"
        >
          <PlayCircle size={18} /> Processar Novo Vídeo
        </button>
      </div>

      <div className="space-y-6">
        {loading && analyses.length === 0 ? (
          <div className="py-20 flex justify-center">
             <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : analyses.map((analysis) => (
          <div key={analysis.id} className="bg-white dark:bg-zinc-900 rounded-2xl border border-gray-100 dark:border-zinc-800 shadow-sm overflow-hidden">
            
            {/* Cabecalho da analise */}
            <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-zinc-800 bg-gray-50/50 dark:bg-zinc-950/30">
              <div className="flex items-center gap-4">
                 <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-inner ${
                   analysis.status === 'completed' ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400' 
                   : analysis.status === 'processing' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-bold' 
                   : 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                 }`}>
                   {analysis.status === 'processing' ? <RefreshCw className="w-6 h-6 animate-spin" /> : 
                    analysis.status === 'completed' ? <BarChart className="w-6 h-6" /> : <Info className="w-6 h-6" />}
                 </div>
                 <div>
                   <h3 className="font-bold text-gray-900 dark:text-white text-lg truncate max-w-sm" title={analysis.video_id}>
                     {analysis.video_id.split('_').slice(2).join('_')}
                   </h3>
                   <div className="flex gap-4 text-xs text-gray-500 mt-1">
                     <span>Duração: {analysis.duration_seconds}s</span>
                     <span>Múltiplos pacientes: {analysis.people_detected}</span>
                     <span>Enviado em: {new Date(analysis.analysis_timestamp).toLocaleDateString('pt-BR')}</span>
                   </div>
                 </div>
              </div>

              <div>
                <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest ${
                   analysis.status === 'completed' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400' 
                   : analysis.status === 'processing' || analysis.status === 'pending' ? 'bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-400'
                   : 'bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-400'
                }`}>
                  {analysis.status === 'processing' ? 'Computando ML...' : analysis.status}
                </span>
              </div>
            </div>

            {/* Corpo / Resultados */}
            <div className="p-6">
              {analysis.status === 'completed' && analysis.results?.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {analysis.results.map((p, idx) => (
                    <div key={idx} className="bg-gray-50 dark:bg-zinc-950/50 rounded-xl p-5 border border-gray-100 dark:border-zinc-800">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="w-8 h-8 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-400 rounded-lg flex items-center justify-center font-bold text-xs">
                           {p.person_id.split('_')[1]}
                        </div>
                        <h4 className="font-semibold text-gray-900 dark:text-zinc-100">Paciente #{idx+1}</h4>
                      </div>

                      <div className="space-y-4">
                        <div className="relative pt-1">
                          <div className="flex mb-2 items-center justify-between">
                            <div><span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/40">Em Pé</span></div>
                            <div className="text-right"><span className="text-xs font-semibold inline-block text-red-600 dark:text-red-400">{p.time_standing_seconds}s</span></div>
                          </div>
                          <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-red-100 dark:bg-zinc-800">
                            <div style={{ width: `${(p.time_standing_seconds/analysis.duration_seconds)*100}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-red-500"></div>
                          </div>
                        </div>

                        <div className="relative pt-1">
                          <div className="flex mb-2 items-center justify-between">
                            <div><span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/40">Sentado/Deitado</span></div>
                            <div className="text-right"><span className="text-xs font-semibold inline-block text-amber-600 dark:text-amber-400">{p.time_sitting_seconds + (p.time_lying_seconds || 0)}s</span></div>
                          </div>
                          <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-amber-100 dark:bg-zinc-800">
                            <div style={{ width: `${((p.time_sitting_seconds + (p.time_lying_seconds || 0))/analysis.duration_seconds)*100}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-amber-500"></div>
                          </div>
                        </div>

                        <div className="relative pt-1">
                          <div className="flex mb-2 items-center justify-between">
                            <div><span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-teal-600 bg-teal-100 dark:text-teal-400 dark:bg-teal-900/40">Movimentação</span></div>
                            <div className="text-right"><span className="text-xs font-semibold inline-block text-teal-600 dark:text-teal-400">{p.time_moving_seconds}s</span></div>
                          </div>
                          <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-teal-100 dark:bg-zinc-800">
                            <div style={{ width: `${(p.time_moving_seconds/analysis.duration_seconds)*100}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-teal-500"></div>
                          </div>
                        </div>
                      </div>

                    </div>
                  ))}
                </div>
              ) : analysis.status === 'failed' ? (
                <div className="text-sm text-red-500 bg-red-50 dark:bg-red-950/20 p-4 rounded-xl border border-red-100 dark:border-red-900/30">
                  <span className="font-bold">Erro de Inferência:</span> {analysis.error_message || "Desconhecido"}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-8 opacity-60">
                  <PieChart className="w-12 h-12 text-gray-400 mb-3" />
                  <p className="text-sm text-gray-500">Os histogramas de postura vão aparecer aqui quando o cálculo finalizar...</p>
                </div>
              )}
            </div>
            
          </div>
        ))}
      </div>


      {showUpload && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-zinc-900 rounded-2xl w-full max-w-lg p-6 shadow-2xl border border-gray-100 dark:border-zinc-800 animate-in zoom-in-95 duration-200">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <UploadVideo className="text-blue-500" />
              Processar Vídeo
            </h2>
            <form onSubmit={handleUpload} className="space-y-4">
              
              <div className="border-2 border-dashed border-gray-300 dark:border-zinc-700 rounded-xl p-8 text-center hover:bg-gray-50 dark:hover:bg-zinc-800/50 transition-colors cursor-pointer relative">
                <input 
                  type="file" 
                  accept=".mp4,.avi,.mov"
                  required
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="text-gray-500 dark:text-zinc-400 font-medium cursor-pointer flex flex-col items-center">
                   {file ? (
                     <>
                      <Video size={32} className="text-blue-500 mb-2" />
                      <span className="text-gray-900 dark:text-zinc-200">{file.name}</span>
                     </>
                   ) : (
                     <>
                      <UploadVideo size={32} className="text-gray-400 mb-2" />
                      <span>Selecione .MP4 gravado pelos leitos</span>
                     </>
                   )}
                </div>
              </div>

              <div className="text-sm text-gray-500 bg-gray-50 dark:bg-zinc-800 p-4 rounded-xl">
                 O processamento ocorrerá em <b>Background</b> pela nossa API FastAPI e o modelo de ML ativo avaliará cada frame para estimar posturas (Múltiplos pacientes simultâneos).
              </div>

              <div className="flex gap-3 justify-end mt-8 pt-4 border-t border-gray-100 dark:border-zinc-800">
                <button 
                  type="button" 
                  disabled={uploading}
                  onClick={() => setShowUpload(false)} 
                  className="px-5 py-2.5 rounded-xl text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-zinc-800 transition-colors font-medium"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  disabled={uploading || !file}
                  className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium transition-colors shadow-blue-600/20 shadow-lg"
                >
                  {uploading ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Transferindo...</>
                  ) : "Iniciar Inferência"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
