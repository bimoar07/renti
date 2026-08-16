package com.example.renti.ui

import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.renti.network.ChatRequest
import com.example.renti.network.ClientContext
import com.example.renti.network.RetrofitClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ChatMessage(val text: String, val isUser: Boolean, val isCrisis: Boolean = false)

class ChatViewModel : ViewModel() {
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Daftar pesan untuk dirender di UI
    val messages = mutableStateListOf<ChatMessage>()

    fun sendMessage(userText: String) {
        if (userText.isBlank()) return

        // 1. Tambahkan pesan user ke layar
        messages.add(ChatMessage(text = userText, isUser = true))
        _isLoading.value = true

        // 2. Siapkan payload sesuai kontrak
        val request = ChatRequest(
            userId = "demo-user-001",
            conversationId = "conversation-001",
            message = userText,
            clientContext = ClientContext()
        )

        // 3. Panggil API secara asinkron
        viewModelScope.launch {
            try {
                val response = RetrofitClient.apiService.sendMessage(request)

                // Cek apakah balasan merupakan peringatan krisis darurat
                val isCrisisMode = response.policyAction == "BLOCK_AND_SIGNPOST"

                messages.add(ChatMessage(
                    text = response.reply,
                    isUser = false,
                    isCrisis = isCrisisMode
                ))
            } catch (e: Exception) {
                messages.add(ChatMessage(
                    text = "Gagal terhubung ke Teman Curhat. Pastikan koneksi aman.",
                    isUser = false,
                    isCrisis = true
                ))
            } finally {
                _isLoading.value = false
            }
        }
    }
}