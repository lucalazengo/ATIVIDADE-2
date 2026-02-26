"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { LayoutDashboard, Users, HardDrive, Video, LogOut, Activity } from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const routes = [
    { name: "Painel Geral", path: "/dashboard", icon: <LayoutDashboard size={20} /> },
    { name: "Pesquisadores", path: "/dashboard/users", icon: <Users size={20} /> },
    { name: "Modelos ML", path: "/dashboard/models", icon: <HardDrive size={20} /> },
    { name: "Vídeos & Inferência", path: "/dashboard/videos", icon: <Video size={20} /> },
  ];

  return (
    <aside className="w-64 bg-white dark:bg-zinc-950 border-r border-gray-100 dark:border-zinc-800 h-screen flex flex-col shadow-sm hidden md:flex">
      <div className="p-6 pb-2">
        <div className="flex items-center gap-3 text-blue-600 mb-8">
          <Activity size={28} />
          <span className="font-bold text-xl tracking-tight text-gray-900 dark:text-white">
            MedVision
          </span>
        </div>
        
        <nav className="space-y-1">
          {routes.map((route) => {
            const active = pathname === route.path;
            return (
              <Link 
                key={route.path} 
                href={route.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  active 
                    ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20 dark:text-blue-400" 
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-zinc-400 dark:hover:bg-zinc-900/50 dark:hover:text-zinc-200"
                }`}
              >
                {route.icon}
                <span className="text-sm">{route.name}</span>
              </Link>
            )
          })}
        </nav>
      </div>

      <div className="mt-auto p-4 border-t border-gray-100 dark:border-zinc-800">
        <div className="flex items-center gap-3 px-4 py-3 mb-2 rounded-xl bg-gray-50 dark:bg-zinc-900">
          <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-700 dark:text-blue-300 font-bold text-xs uppercase">
            {user?.full_name ? user.full_name.charAt(0) : "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {user?.full_name || "Pesquisador"}
            </p>
            <p className="text-xs text-gray-500 dark:text-zinc-500 truncate">
              {user?.email || "carregando..."}
            </p>
          </div>
        </div>
        
        <button 
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/30 rounded-xl transition-colors"
        >
          <LogOut size={18} />
          Sair do sistema
        </button>
      </div>
    </aside>
  );
}
