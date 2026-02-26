"use client";

import { useAuth } from "@/contexts/AuthContext";
import { Activity, ClockLine, Users2, Database, Camera } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const { user } = useAuth();
  
  // Dummy dashboard data states for prototype
  const [activeModel, setActiveModel] = useState<{name: string, framework: string} | null>(null);

  useEffect(() => {
    api.get("/models/active").then(res => {
      setActiveModel({name: res.data.filename, framework: res.data.framework});
    }).catch(e => {
        // No active model found
    });
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
      
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
            Painel Geral
          </h1>
          <p className="text-gray-500 mt-2 text-lg">
            Bem-vindo de volta, pesquisador {user?.full_name?.split(' ')[0]}.
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-zinc-800 flex items-start gap-4 hover:shadow-md transition-shadow">
          <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-xl text-blue-600 dark:text-blue-400">
            <Camera size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-zinc-400">Vídeos Processados</p>
            <h3 className="text-2xl font-bold mt-1 text-gray-900 dark:text-white">142</h3>
          </div>
        </div>
        
        <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-zinc-800 flex items-start gap-4 hover:shadow-md transition-shadow">
          <div className="bg-indigo-100 dark:bg-indigo-900/30 p-3 rounded-xl text-indigo-600 dark:text-indigo-400">
            <Users2 size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-zinc-400">Pacientes Detectados</p>
            <h3 className="text-2xl font-bold mt-1 text-gray-900 dark:text-white">318</h3>
          </div>
        </div>

        <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-zinc-800 flex items-start gap-4 hover:shadow-md transition-shadow">
          <div className="bg-emerald-100 dark:bg-emerald-900/30 p-3 rounded-xl text-emerald-600 dark:text-emerald-400">
            <Database size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-zinc-400">Modelos Treinados</p>
            <h3 className="text-2xl font-bold mt-1 text-gray-900 dark:text-white">4</h3>
          </div>
        </div>

        <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-zinc-800 flex items-start gap-4 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="absolute -right-4 -top-8 opacity-10 blur-xl">
             <Activity size={100} className="text-blue-500" />
          </div>
          
          <div className="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-xl text-purple-600 dark:text-purple-400 z-10">
            <Activity size={24} />
          </div>
          <div className="z-10">
            <p className="text-sm font-medium text-gray-500 dark:text-zinc-400">Modelo Ativo</p>
            <h3 className="text-lg font-bold mt-1 text-gray-900 dark:text-white truncate max-w-[120px]" title={activeModel?.name}>
              {activeModel ? activeModel.framework.toUpperCase() : "Nenhum"}
            </h3>
          </div>
        </div>
      </div>

    </div>
  );
}
