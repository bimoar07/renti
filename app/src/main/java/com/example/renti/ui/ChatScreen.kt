package com.example.renti.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(viewModel: ChatViewModel = viewModel()) {
    var inputText by remember { mutableStateOf("") }
    val isLoading by viewModel.isLoading.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Teman Curhat") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .fillMaxSize()
        ) {
            // Area Obrolan
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(viewModel.messages) { msg ->
                    ChatBubble(msg)
                }
            }

            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier
                        .align(Alignment.CenterHorizontally)
                        .padding(8.dp)
                )
            }

            // Area Input Teks
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Ketik curhatanmu...") },
                    shape = RoundedCornerShape(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Button(
                    onClick = {
                        viewModel.sendMessage(inputText)
                        inputText = ""
                    },
                    enabled = !isLoading && inputText.isNotBlank()
                ) {
                    Text("Kirim")
                }
            }
        }
    }
}

@Composable
fun ChatBubble(message: ChatMessage) {
    val bubbleColor = when {
        message.isCrisis -> MaterialTheme.colorScheme.errorContainer // Merah jika krisis
        message.isUser -> MaterialTheme.colorScheme.primary          // Oranye jika user
        else -> MaterialTheme.colorScheme.surfaceVariant             // Abu-abu jika AI
    }

    val textColor = when {
        message.isCrisis -> MaterialTheme.colorScheme.onErrorContainer
        message.isUser -> MaterialTheme.colorScheme.onPrimary
        else -> MaterialTheme.colorScheme.onSurfaceVariant
    }

    Box(
        modifier = Modifier.fillMaxWidth(),
        contentAlignment = if (message.isUser) Alignment.CenterEnd else Alignment.CenterStart
    ) {
        Text(
            text = message.text,
            color = textColor,
            modifier = Modifier
                .background(
                    color = bubbleColor,
                    shape = RoundedCornerShape(16.dp)
                )
                .padding(12.dp)
        )
    }
}