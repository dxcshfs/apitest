/**
 * API测试工具自定义脚本
 */

// 在文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 自动关闭警告消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000); // 5秒后自动关闭
    });

    // 格式化JSON输入
    const formatJsonBtn = document.getElementById('format-json-btn');
    if (formatJsonBtn) {
        formatJsonBtn.addEventListener('click', function() {
            const headersTextarea = document.getElementById('headers');
            if (headersTextarea) {
                try {
                    const json = JSON.parse(headersTextarea.value);
                    headersTextarea.value = JSON.stringify(json, null, 2);
                } catch (e) {
                    alert('无效的JSON格式');
                }
            }
        });
    }

    // 复制响应内容
    const copyResponseBtn = document.getElementById('copy-response-btn');
    if (copyResponseBtn) {
        copyResponseBtn.addEventListener('click', function() {
            const responseData = document.getElementById('response-data');
            if (responseData) {
                const text = responseData.textContent;
                navigator.clipboard.writeText(text)
                    .then(() => {
                        // 显示复制成功提示
                        const originalText = copyResponseBtn.innerHTML;
                        copyResponseBtn.innerHTML = '<i class="fas fa-check"></i> 已复制';
                        setTimeout(() => {
                            copyResponseBtn.innerHTML = originalText;
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('复制失败:', err);
                        alert('复制失败');
                    });
            }
        });
    }

    // 美化JSON响应
    function beautifyJson() {
        const jsonElements = document.querySelectorAll('.json-response');
        jsonElements.forEach(function(element) {
            try {
                const text = element.textContent;
                if (text && text.trim() && text.trim() !== 'null') {
                    const json = JSON.parse(text);
                    element.textContent = JSON.stringify(json, null, 2);
                }
            } catch (e) {
                // 不是有效的JSON，保持原样
                console.log('不是有效的JSON:', e);
            }
        });
    }

    // 页面加载时美化JSON
    beautifyJson();

    // 添加参数行时的动画效果
    function addParamWithAnimation(container, html) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const newRow = tempDiv.firstElementChild;
        newRow.style.opacity = '0';
        container.appendChild(newRow);
        
        // 触发重绘
        void newRow.offsetWidth;
        
        // 添加过渡效果
        newRow.style.transition = 'opacity 0.3s ease';
        newRow.style.opacity = '1';
    }

    // 添加参数按钮
    const addParamBtn = document.getElementById('add-param-btn');
    if (addParamBtn) {
        addParamBtn.addEventListener('click', function() {
            const paramsContainer = document.getElementById('params-container');
            const paramHtml = `
                <div class="param-row">
                    <div class="input-group mb-2">
                        <input type="text" class="form-control" name="param_name[]" placeholder="参数名">
                        <input type="text" class="form-control" name="param_value[]" placeholder="默认值">
                        <select class="form-select" name="param_type[]">
                            <option value="query">查询参数</option>
                            <option value="body">请求体参数</option>
                        </select>
                        <button type="button" class="btn btn-outline-danger remove-param">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
            addParamWithAnimation(paramsContainer, paramHtml);
        });
    }

    // 删除参数行
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-param') || e.target.closest('.remove-param')) {
            const btn = e.target.classList.contains('remove-param') ? e.target : e.target.closest('.remove-param');
            const row = btn.closest('.param-row');
            
            // 添加淡出效果
            row.style.transition = 'opacity 0.3s ease';
            row.style.opacity = '0';
            
            // 等待动画完成后移除元素
            setTimeout(function() {
                row.remove();
            }, 300);
        }
    });

    // 表单验证
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredInputs.forEach(function(input) {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('is-invalid');
                    
                    // 添加验证反馈
                    const feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = '此字段为必填项';
                    
                    // 如果还没有反馈元素，则添加
                    if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('invalid-feedback')) {
                        input.parentNode.insertBefore(feedback, input.nextElementSibling);
                    }
                } else {
                    input.classList.remove('is-invalid');
                    
                    // 移除验证反馈
                    if (input.nextElementSibling && input.nextElementSibling.classList.contains('invalid-feedback')) {
                        input.nextElementSibling.remove();
                    }
                }
            });
            
            // 验证JSON格式
            const headersTextarea = document.getElementById('headers');
            if (headersTextarea && headersTextarea.value.trim()) {
                try {
                    JSON.parse(headersTextarea.value);
                    headersTextarea.classList.remove('is-invalid');
                    
                    // 移除验证反馈
                    if (headersTextarea.nextElementSibling && headersTextarea.nextElementSibling.classList.contains('invalid-feedback')) {
                        headersTextarea.nextElementSibling.remove();
                    }
                } catch (error) {
                    isValid = false;
                    headersTextarea.classList.add('is-invalid');
                    
                    // 添加验证反馈
                    const feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = '请输入有效的JSON格式';
                    
                    // 如果还没有反馈元素，则添加
                    if (!headersTextarea.nextElementSibling || !headersTextarea.nextElementSibling.classList.contains('invalid-feedback')) {
                        headersTextarea.parentNode.insertBefore(feedback, headersTextarea.nextElementSibling);
                    }
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
});