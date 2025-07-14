import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv
from database import *

class BookManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("图书管理系统")
        self.root.geometry("1000x850")
        self.root.resizable(True, True)
        
        # 初始化样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('微软雅黑', 10))
        self.style.configure("TLabel", font=('微软雅黑', 10))
        self.style.configure("TEntry", font=('微软雅黑', 10))
        self.style.configure("Treeview", font=('微软雅黑', 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=('微软雅黑', 11, 'bold'))
        
        # 创建选项卡
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建各个功能页
        self.create_book_management_tab()
        self.create_search_tab()
        self.create_borrow_return_tab()
        
        # 初始化数据库
        success, msg = initialize_database()
        if not success:
            messagebox.showerror("数据库错误", msg)
    
    def create_book_management_tab(self):
        """创建图书管理选项卡（增加ID输入）"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="图书管理")
        
        # 使用网格布局管理器减少空白
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 添加图书部分
        add_frame = ttk.LabelFrame(main_frame, text="添加图书")
        add_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        ttk.Label(add_frame, text="ID (可选):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.add_id = ttk.Entry(add_frame, width=10)
        self.add_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="书名:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.book_name = ttk.Entry(add_frame, width=30)
        self.book_name.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="作者:").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.author_name = ttk.Entry(add_frame, width=30)
        self.author_name.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(add_frame, text="添加图书", command=self.add_book).grid(row=0, column=6, padx=10, pady=5)
        
        # 批量添加图书部分
        batch_frame = ttk.LabelFrame(main_frame, text="批量添加图书")
        batch_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # 文本输入框
        ttk.Label(batch_frame, text="批量输入 (每行格式: 书名,作者):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.batch_text = tk.Text(batch_frame, width=80, height=6, font=('微软雅黑', 10))
        self.batch_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')
        
        # 滚动条
        scrollbar = ttk.Scrollbar(batch_frame, command=self.batch_text.yview)
        self.batch_text.config(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=3, sticky='ns')
        
        # 按钮区域
        button_frame = ttk.Frame(batch_frame)
        button_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky='ew')
        
        ttk.Button(button_frame, text="导入CSV文件", command=self.import_csv).pack(side='left', padx=5)
        ttk.Button(button_frame, text="清空输入", command=self.clear_batch_input).pack(side='left', padx=5)
        ttk.Button(button_frame, text="批量添加", command=self.add_books_batch).pack(side='right', padx=5)
        
        # 更新图书部分
        update_frame = ttk.LabelFrame(main_frame, text="更新图书")
        update_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        ttk.Label(update_frame, text="原图书ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.update_id = ttk.Entry(update_frame, width=10)
        self.update_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(update_frame, text="新ID (可选):").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.new_id = ttk.Entry(update_frame, width=10)
        self.new_id.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(update_frame, text="新书名 (可选):").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.new_book_name = ttk.Entry(update_frame, width=30)
        self.new_book_name.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(update_frame, text="新作者 (可选):").grid(row=0, column=6, padx=5, pady=5, sticky='e')
        self.new_author_name = ttk.Entry(update_frame, width=30)
        self.new_author_name.grid(row=0, column=7, padx=5, pady=5)
        
        ttk.Button(update_frame, text="更新图书", command=self.update_book).grid(row=0, column=8, padx=10, pady=5)
        
        # 删除图书部分 - 重构为搜索删除
        delete_frame = ttk.LabelFrame(main_frame, text="删除图书")
        delete_frame.grid(row=3, column=0, sticky='nsew', padx=5, pady=5)
        
        # 搜索区域
        search_frame = ttk.Frame(delete_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索条件 (ID/书名/作者):").pack(side='left', padx=5, pady=5)
        self.delete_search = ttk.Entry(search_frame, width=40)
        self.delete_search.pack(side='left', padx=5, pady=5, fill='x', expand=True)
        
        ttk.Button(search_frame, text="搜索", command=self.search_for_delete).pack(side='left', padx=5, pady=5)
        
        # 结果表格
        columns = ("select", "id", "bname", "writer")
        self.delete_tree = ttk.Treeview(
            delete_frame, 
            columns=columns, 
            show="headings",
            selectmode="none",  # 禁用默认选择
            height=8
        )
        
        # 设置列标题
        self.delete_tree.heading("select", text="选择")
        self.delete_tree.heading("id", text="ID")
        self.delete_tree.heading("bname", text="书名")
        self.delete_tree.heading("writer", text="作者")
        
        # 设置列宽
        self.delete_tree.column("select", width=50, anchor='center')
        self.delete_tree.column("id", width=50, anchor='center')
        self.delete_tree.column("bname", width=250)
        self.delete_tree.column("writer", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(delete_frame, orient="vertical", command=self.delete_tree.yview)
        self.delete_tree.configure(yscrollcommand=scrollbar.set)
        
        # 使用网格布局表格
        self.delete_tree.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=(0, 5), pady=5)
        
        # 复选框状态字典
        self.checkbox_vars = {}
        
        # 操作按钮区域
        button_frame = ttk.Frame(delete_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        # 全选复选框
        self.select_all_var = tk.BooleanVar()
        ttk.Checkbutton(button_frame, text="全选", variable=self.select_all_var, 
                        command=self.toggle_select_all).pack(side='left', padx=5, pady=5)
        
        # 删除按钮
        ttk.Button(button_frame, text="删除选中", command=self.delete_selected).pack(side='left', padx=5, pady=5)
        ttk.Button(button_frame, text="全部删除", command=self.delete_all).pack(side='left', padx=5, pady=5)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        for i in range(4):
            main_frame.rowconfigure(i, weight=0)
        main_frame.rowconfigure(3, weight=1)  # 删除区域可扩展
    
    def create_search_tab(self):
        """创建图书查询选项卡（优化布局）"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="图书查询")
        
        # 使用网格布局管理器
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 搜索框
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索条件:").pack(side='left', padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side='left', padx=5, pady=5, fill='x', expand=True)
        
        ttk.Button(search_frame, text="搜索", command=self.search_books).pack(side='left', padx=5, pady=5)
        ttk.Button(search_frame, text="显示全部", command=lambda: self.search_books("")).pack(side='left', padx=5, pady=5)
        
        # 结果表格
        columns = ("id", "bname", "writer")
        self.result_tree = ttk.Treeview(
            main_frame, 
            columns=columns, 
            show="headings",
            selectmode="browse"
        )
        
        # 设置列标题
        self.result_tree.heading("id", text="ID")
        self.result_tree.heading("bname", text="书名")
        self.result_tree.heading("writer", text="作者")
        
        # 设置列宽
        self.result_tree.column("id", width=50, anchor='center')
        self.result_tree.column("bname", width=300)
        self.result_tree.column("writer", width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        # 使用网格布局表格
        self.result_tree.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        scrollbar.grid(row=1, column=1, sticky='ns', pady=5)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 初始显示所有图书
        self.search_books("")
    
    def create_borrow_return_tab(self):
        """创建借阅归还选项卡（优化布局）"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="借阅管理")
        
        # 使用网格布局管理器
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 借阅部分
        borrow_frame = ttk.LabelFrame(main_frame, text="借阅图书")
        borrow_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Label(borrow_frame, text="图书ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.borrow_id = ttk.Entry(borrow_frame, width=10)
        self.borrow_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(borrow_frame, text="借阅人:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.borrower = ttk.Entry(borrow_frame, width=30)
        self.borrower.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(borrow_frame, text="借阅", command=self.borrow_book).grid(row=0, column=4, padx=10, pady=5)
        
        # 归还部分
        return_frame = ttk.LabelFrame(main_frame, text="归还图书")
        return_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Label(return_frame, text="图书ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.return_id = ttk.Entry(return_frame, width=10)
        self.return_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(return_frame, text="归还", command=self.return_book).grid(row=0, column=2, padx=10, pady=5)
        
        # 借阅记录表格
        columns = ("id", "book_id", "bname", "borrower", "borrow_date", "return_date")
        self.borrow_tree = ttk.Treeview(
            main_frame, 
            columns=columns, 
            show="headings",
            selectmode="browse"
        )
        
        # 设置列标题
        self.borrow_tree.heading("id", text="记录ID")
        self.borrow_tree.heading("book_id", text="图书ID")
        self.borrow_tree.heading("bname", text="书名")
        self.borrow_tree.heading("borrower", text="借阅人")
        self.borrow_tree.heading("borrow_date", text="借阅日期")
        self.borrow_tree.heading("return_date", text="归还日期")
        
        # 设置列宽
        self.borrow_tree.column("id", width=60, anchor='center')
        self.borrow_tree.column("book_id", width=60, anchor='center')
        self.borrow_tree.column("bname", width=200)
        self.borrow_tree.column("borrower", width=100)
        self.borrow_tree.column("borrow_date", width=100)
        self.borrow_tree.column("return_date", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.borrow_tree.yview)
        self.borrow_tree.configure(yscrollcommand=scrollbar.set)
        
        # 使用网格布局表格
        self.borrow_tree.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        scrollbar.grid(row=2, column=1, sticky='ns', pady=5)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 加载借阅记录
        self.load_borrow_records()
    
    def add_book(self):
        """添加图书操作（自动选择最小可用ID）"""
        bname = self.book_name.get().strip()
        writer = self.author_name.get().strip()
        book_id = self.add_id.get().strip()
        
        # 处理ID输入
        book_id_value = None
        if book_id:
            try:
                book_id_value = int(book_id)
            except ValueError:
                messagebox.showwarning("输入错误", "ID必须为数字")
                return
        
        success, msg = add_book(bname, writer, book_id_value)
        if success:
            messagebox.showinfo("成功", msg)
            self.add_id.delete(0, tk.END)
            self.book_name.delete(0, tk.END)
            self.author_name.delete(0, tk.END)
            self.search_books("")  # 刷新查询结果
        else:
            messagebox.showerror("错误", msg)
    
    def add_books_batch(self):
        """批量添加图书操作"""
        # 获取文本内容
        text = self.batch_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("输入错误", "请输入批量添加的图书数据")
            return
        
        # 解析文本
        book_list = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',', 1)  # 只分割一次，因为作者名可能包含逗号
            if len(parts) < 2:
                continue
            bname, writer = parts
            book_list.append((bname, writer))
        
        if not book_list:
            messagebox.showwarning("输入错误", "未找到有效的图书数据")
            return
        
        # 确认添加
        if not messagebox.askyesno("确认", f"确定要添加 {len(book_list)} 本图书吗？"):
            return
        
        # 调用批量添加函数
        success, msg = add_books_in_batch(book_list)
        if success:
            messagebox.showinfo("成功", msg)
            self.batch_text.delete("1.0", tk.END)  # 清空输入框
            self.search_books("")  # 刷新查询结果
        else:
            messagebox.showerror("错误", msg)
    
    def import_csv(self):
        """导入CSV文件"""
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                # 跳过标题行（如果有）
                next(reader, None)
                
                # 读取数据
                book_list = []
                for row in reader:
                    if len(row) >= 2:
                        bname, writer = row[0], row[1]
                        book_list.append((bname, writer))
                
                if not book_list:
                    messagebox.showwarning("导入错误", "CSV文件中未找到有效数据")
                    return
                
                # 显示在文本框中
                self.batch_text.delete("1.0", tk.END)
                for bname, writer in book_list:
                    self.batch_text.insert(tk.END, f"{bname},{writer}\n")
                
                messagebox.showinfo("导入成功", f"成功导入 {len(book_list)} 条记录")
        except Exception as e:
            messagebox.showerror("导入错误", f"导入CSV文件失败: {e}")
    
    def clear_batch_input(self):
        """清空批量输入框"""
        self.batch_text.delete("1.0", tk.END)
    
    def update_book(self):
        """更新图书操作（支持修改ID）"""
        try:
            book_id = int(self.update_id.get().strip())
        except ValueError:
            messagebox.showwarning("输入错误", "图书ID必须为数字")
            return
        
        new_bname = self.new_book_name.get().strip()
        new_writer = self.new_author_name.get().strip()
        new_id_str = self.new_id.get().strip()
        
        # 处理新ID输入
        new_id_value = None
        if new_id_str:
            try:
                new_id_value = int(new_id_str)
            except ValueError:
                messagebox.showwarning("输入错误", "新ID必须为数字")
                return
        
        success, msg = update_book(book_id, new_bname, new_writer, new_id_value)
        if success:
            messagebox.showinfo("成功", msg)
            self.update_id.delete(0, tk.END)
            self.new_id.delete(0, tk.END)
            self.new_book_name.delete(0, tk.END)
            self.new_author_name.delete(0, tk.END)
            self.search_books("")  # 刷新查询结果
            self.load_borrow_records()  # 刷新借阅记录
        else:
            messagebox.showerror("错误", msg)
    
    def search_for_delete(self):
        """为删除功能搜索图书"""
        keyword = self.delete_search.get().strip()
        success, result = search_books(keyword)
        
        if success:
            # 清空现有数据和复选框状态
            for item in self.delete_tree.get_children():
                self.delete_tree.delete(item)
            self.checkbox_vars.clear()
            
            # 插入新数据
            for book in result:
                book_id, bname, writer = book
                # 创建复选框变量
                var = tk.BooleanVar(value=False)
                self.checkbox_vars[book_id] = var
                
                # 插入带复选框的行
                self.delete_tree.insert("", tk.END, values=(
                    " ",  # 复选框占位符
                    book_id, 
                    bname, 
                    writer
                ), tags=(str(book_id),))
                
                # 绑定点击事件
                self.delete_tree.tag_bind(str(book_id), "<Button-1>", self.on_checkbox_click)
        else:
            messagebox.showerror("错误", result)
    
    def on_checkbox_click(self, event):
        """处理复选框点击事件"""
        # 获取点击的行
        item = self.delete_tree.identify_row(event.y)
        if not item:
            return
        
        # 获取图书ID
        item_id = self.delete_tree.item(item, "tags")[0]
        book_id = int(item_id)
        
        # 切换复选框状态
        current_value = self.checkbox_vars[book_id].get()
        self.checkbox_vars[book_id].set(not current_value)
        
        # 更新显示
        self.update_checkbox_display(item, not current_value)
    
    def update_checkbox_display(self, item, checked):
        """更新复选框显示状态"""
        # 获取当前值
        values = list(self.delete_tree.item(item, "values"))
        
        # 更新复选框显示
        values[0] = "✓" if checked else " "
        
        # 设置新值
        self.delete_tree.item(item, values=values)
    
    def toggle_select_all(self):
        """全选/取消全选所有复选框"""
        all_checked = self.select_all_var.get()
        
        # 更新所有复选框状态
        for book_id, var in self.checkbox_vars.items():
            var.set(all_checked)
        
        # 更新所有行的显示
        for item in self.delete_tree.get_children():
            item_id = self.delete_tree.item(item, "tags")[0]
            self.update_checkbox_display(item, all_checked)
    
    def delete_selected(self):
        """删除选中的图书"""
        # 获取选中的图书ID
        selected_ids = [book_id for book_id, var in self.checkbox_vars.items() if var.get()]
        
        if not selected_ids:
            messagebox.showwarning("提示", "请先选择要删除的图书")
            return
        
        if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_ids)} 本图书吗？"):
            return
        
        success, msg = delete_books(selected_ids)
        if success:
            messagebox.showinfo("成功", msg)
            # 刷新数据和显示
            self.search_for_delete()
            self.search_books("")
            self.load_borrow_records()
        else:
            messagebox.showerror("错误", msg)
    
    def delete_all(self):
        """删除所有显示的图书"""
        # 获取当前显示的所有图书ID
        all_ids = list(self.checkbox_vars.keys())
        
        if not all_ids:
            messagebox.showwarning("提示", "没有可删除的图书")
            return
        
        if not messagebox.askyesno("确认删除", f"确定要删除当前显示的所有 {len(all_ids)} 本图书吗？"):
            return
        
        success, msg = delete_books(all_ids)
        if success:
            messagebox.showinfo("成功", msg)
            # 刷新数据和显示
            self.search_for_delete()
            self.search_books("")
            self.load_borrow_records()
        else:
            messagebox.showerror("错误", msg)
    
    def search_books(self, keyword=None):
        """搜索图书操作"""
        if keyword is None:
            keyword = self.search_entry.get().strip()
        
        success, result = search_books(keyword)
        
        if success:
            # 清空现有数据
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 插入新数据
            for book in result:
                self.result_tree.insert("", tk.END, values=book)
        else:
            messagebox.showerror("错误", result)
    
    def borrow_book(self):
        """借阅图书操作"""
        try:
            book_id = int(self.borrow_id.get().strip())
        except ValueError:
            messagebox.showwarning("输入错误", "图书ID必须为数字")
            return
        
        borrower = self.borrower.get().strip()
        if not borrower:
            messagebox.showwarning("输入错误", "借阅人不能为空")
            return
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # 检查图书是否存在
            cursor.execute("SELECT id FROM book WHERE id = %s", (book_id,))
            if not cursor.fetchone():
                messagebox.showerror("错误", f"图书ID {book_id} 不存在")
                return
            
            # 检查是否已借出未归还
            cursor.execute("""
            SELECT id FROM borrow_record 
            WHERE book_id = %s AND return_date IS NULL
            """, (book_id,))
            if cursor.fetchone():
                messagebox.showerror("错误", f"图书ID {book_id} 已被借出未归还")
                return
            
            # 添加借阅记录
            today = datetime.date.today()
            sql = """
            INSERT INTO borrow_record (book_id, borrower, borrow_date) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (book_id, borrower, today))
            conn.commit()
            
            messagebox.showinfo("成功", f"借阅成功：图书ID {book_id} 借给 {borrower}")
            self.borrow_id.delete(0, tk.END)
            self.borrower.delete(0, tk.END)
            self.load_borrow_records()  # 刷新借阅记录
        except Exception as e:
            messagebox.showerror("错误", f"借阅失败: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def return_book(self):
        """归还图书操作"""
        try:
            book_id = int(self.return_id.get().strip())
        except ValueError:
            messagebox.showwarning("输入错误", "图书ID必须为数字")
            return
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # 获取未归还的记录
            cursor.execute("""
            SELECT id FROM borrow_record 
            WHERE book_id = %s AND return_date IS NULL
            ORDER BY borrow_date DESC 
            LIMIT 1
            """, (book_id,))
            record = cursor.fetchone()
            
            if not record:
                messagebox.showerror("错误", f"找不到图书ID {book_id} 的有效借阅记录")
                return
            
            # 更新归还日期
            today = datetime.date.today()
            cursor.execute("""
            UPDATE borrow_record SET return_date = %s 
            WHERE id = %s
            """, (today, record[0]))
            conn.commit()
            
            messagebox.showinfo("成功", f"归还成功：图书ID {book_id}")
            self.return_id.delete(0, tk.END)
            self.load_borrow_records()  # 刷新借阅记录
        except Exception as e:
            messagebox.showerror("错误", f"归还失败: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def load_borrow_records(self):
        """加载借阅记录"""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # 执行查询（关联图书表获取书名）
            sql = """
            SELECT 
                br.id, br.book_id, b.bname, br.borrower, 
                br.borrow_date, br.return_date 
            FROM borrow_record br
            JOIN book b ON br.book_id = b.id
            ORDER BY br.borrow_date DESC
            """
            cursor.execute(sql)
            records = cursor.fetchall()
            
            # 清空现有数据
            for item in self.borrow_tree.get_children():
                self.borrow_tree.delete(item)
            
            # 插入新数据
            for record in records:
                self.borrow_tree.insert("", tk.END, values=record)
        except Exception as e:
            messagebox.showerror("错误", f"加载借阅记录失败: {e}")
        finally:
            cursor.close()
            conn.close()