"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Plus, Pencil, Trash2, Mail, Loader2 } from "lucide-react";

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Modal states
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ id: 0, full_name: "", email: "", password: "", is_active: true });
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await api.get("/users");
      setUsers(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isEditing) {
        const payload: any = { full_name: formData.full_name, email: formData.email, is_active: formData.is_active };
        if (formData.password) payload.password = formData.password; // only update password if provided
        
        await api.put(`/users/${formData.id}`, payload);
      } else {
        await api.post("/users", {
          full_name: formData.full_name,
          email: formData.email,
          password: formData.password,
          is_active: formData.is_active
        });
      }
      setShowModal(false);
      fetchUsers();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erro inesperado.");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Tem certeza que deseja excluir o pesquisador?")) return;
    try {
      await api.delete(`/users/${id}`);
      fetchUsers();
    } catch (e) {
      console.error(e);
    }
  };

  const openNewUser = () => {
    setFormData({ id: 0, full_name: "", email: "", password: "", is_active: true });
    setIsEditing(false);
    setShowModal(true);
  };

  const openEditUser = (u: User) => {
    setFormData({ id: u.id, full_name: u.full_name, email: u.email, password: "", is_active: u.is_active });
    setIsEditing(true);
    setShowModal(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white dark:bg-zinc-900 p-6 rounded-2xl border border-gray-100 dark:border-zinc-800 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
            Equipe Científica
          </h1>
          <p className="text-gray-500 text-sm mt-1">Gerencie os acessos ao modelo de visão computacional.</p>
        </div>
        <button 
          onClick={openNewUser}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium transition-colors"
        >
          <Plus size={18} /> Novo Pesquisador
        </button>
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-2xl border border-gray-100 dark:border-zinc-800 shadow-sm overflow-hidden p-6 relative min-h-[400px]">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-zinc-900/50 backdrop-blur-sm z-10">
             <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : null}

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 dark:border-zinc-800 text-gray-500 dark:text-zinc-400 text-sm font-medium">
                <th className="pb-3 pl-4">Identificação</th>
                <th className="pb-3">Contato</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 pr-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50 dark:divide-zinc-800/80">
              {users.map(u => (
                <tr key={u.id} className="hover:bg-gray-50/50 dark:hover:bg-zinc-800/50 transition-colors">
                  <td className="py-4 pl-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold">
                        {u.full_name.charAt(0)}
                      </div>
                      <span className="font-medium text-gray-900 dark:text-zinc-100">{u.full_name}</span>
                    </div>
                  </td>
                  <td className="py-4">
                    <div className="flex items-center gap-2 text-gray-600 dark:text-zinc-400 text-sm">
                      <Mail size={16} /> {u.email}
                    </div>
                  </td>
                  <td className="py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${u.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
                      {u.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="py-4 pr-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                       <button onClick={() => openEditUser(u)} className="p-2 text-gray-400 hover:bg-gray-100 dark:hover:bg-zinc-800 rounded-lg transition-colors">
                          <Pencil size={18} />
                       </button>
                       <button onClick={() => handleDelete(u.id)} className="p-2 text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors">
                          <Trash2 size={18} />
                       </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-white dark:bg-zinc-900 rounded-2xl w-full max-w-md p-6 shadow-2xl border border-gray-100 dark:border-zinc-800 animate-in slide-in-from-bottom-4 duration-300">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
              {isEditing ? "Editar Pesquisador" : "Novo Pesquisador"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Nome Completo</label>
                <input required autoFocus value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} className="w-full border border-gray-200 dark:border-zinc-700 rounded-xl px-4 py-2 bg-transparent dark:text-white focus:ring-2 focus:ring-blue-500" />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">E-mail</label>
                <input required type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full border border-gray-200 dark:border-zinc-700 rounded-xl px-4 py-2 bg-transparent dark:text-white focus:ring-2 focus:ring-blue-500" />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                  Senha {isEditing && <span className="text-xs text-gray-400 font-normal">(deixe em branco para manter)</span>}
                </label>
                <input required={!isEditing} minLength={6} type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} className="w-full border border-gray-200 dark:border-zinc-700 rounded-xl px-4 py-2 bg-transparent dark:text-white focus:ring-2 focus:ring-blue-500" />
              </div>

              <div className="flex items-center gap-2 mt-4 pt-2">
                 <input type="checkbox" id="isActive" checked={formData.is_active} onChange={e => setFormData({...formData, is_active: e.target.checked})} className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                 <label htmlFor="isActive" className="text-sm font-medium text-gray-700 dark:text-gray-300">Liberar Acesso (Ativo)</label>
              </div>

              <div className="flex gap-3 justify-end mt-8">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-zinc-800 transition-colors font-medium">Cancelar</button>
                <button type="submit" className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors">
                  {isEditing ? "Salvar Alterações" : "Cadastrar Acesso"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
