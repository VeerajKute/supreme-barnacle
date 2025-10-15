# DhanHQ API Integration Guide

## 🎯 **Official DhanHQ API v2 Integration**

This document outlines the proper integration with [DhanHQ API v2](https://dhanhq.co/docs/v2/) for the Order Flow Visualizer, ensuring compliance with official specifications.

## 🔐 **Authentication Setup**

### **1. Get Access Token**

#### **Method 1: Direct Access Token (Recommended)**
1. Login to [web.dhan.co](https://web.dhan.co/)
2. Go to **My Profile** → **Access DhanHQ APIs**
3. Generate **Access Token** (valid for 24 hours)
4. Copy the token to your `.env` file

#### **Method 2: API Key & Secret (OAuth Flow)**
1. In **Access DhanHQ APIs** section, toggle to **API key**
2. Enter **App name**, **Redirect URL**, and **Postback URL**
3. Follow the 3-step OAuth process:
   - **Step 1**: Generate Consent
   - **Step 2**: Browser-based login
   - **Step 3**: Consume Consent to get access token

### **2. Environment Configuration**

```bash
# .env file
DHAN_API_KEY=your_access_token_here
DHAN_CLIENT_ID=your_dhan_client_id_here
DHAN_WEBSOCKET_URL=wss://api.dhanhq.co/v2/ws
```

## 📡 **WebSocket Integration**

### **Connection Headers**
```python
headers = {
    "access-token": DHAN_API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}
```

### **Subscription Format**
```python
subscribe_msg = {
    "action": "subscribe",
    "instrument_token": "2885633",
    "feed_type": "full_market_depth",
    "dhanClientId": DHAN_CLIENT_ID,
    "segment": "NSE_EQ"
}
```

### **Message Types**
- `market_depth` - Full market depth data
- `tick` - Tick-by-tick data
- `quote` - Live quote updates
- `error` - Error messages

## 🔌 **API Endpoints**

### **Market Data APIs**

#### **1. Live Market Feed**
```bash
GET https://api.dhan.co/v2/market/quote
Headers: access-token: {your_token}
Params: symbol=RELIANCE&segment=NSE_EQ
```

#### **2. Full Market Depth**
```bash
WebSocket: wss://api.dhanhq.co/v2/ws
Message: {"action": "subscribe", "instrument_token": "2885633", "feed_type": "full_market_depth"}
```

#### **3. Historical Data**
```bash
GET https://api.dhan.co/v2/historical
Headers: access-token: {your_token}
Params: symbol=RELIANCE&segment=NSE_EQ&from=2024-01-01&to=2024-01-31
```

#### **4. Option Chain**
```bash
GET https://api.dhan.co/v2/option-chain
Headers: access-token: {your_token}
Params: symbol=NIFTY&expiryDate=2024-01-25
```

## 🏗️ **Implementation Updates**

### **Backend Changes Made:**

1. **Authentication Headers**
   ```python
   # OLD (incorrect)
   headers = {
       "Authorization": f"Bearer {DHAN_API_KEY}",
       "X-API-SECRET": DHAN_API_SECRET
   }
   
   # NEW (correct)
   headers = {
       "access-token": DHAN_API_KEY,
       "Accept": "application/json",
       "Content-Type": "application/json"
   }
   ```

2. **WebSocket Subscription**
   ```python
   subscribe_msg = {
       "action": "subscribe",
       "instrument_token": symbol_info["token"],
       "feed_type": "full_market_depth",
       "dhanClientId": os.getenv("DHAN_CLIENT_ID", ""),
       "segment": "NSE_EQ"
   }
   ```

3. **Message Processing**
   ```python
   # Added support for DhanHQ message types
   if message_type == "market_depth":
       await self.process_market_depth(data)
   elif message_type == "tick":
       await self.process_tick(data)
   elif message_type == "quote":
       await self.process_quote(data)
   elif message_type == "error":
       logger.error(f"DhanHQ WebSocket error: {data.get('message')}")
   ```

### **Symbol Manager Updates:**

1. **DhanHQ API Integration**
   ```python
   async def _fetch_from_dhanhq_api(self, symbol: str) -> Optional[Dict]:
       url = "https://api.dhan.co/v2/market/quote"
       headers = {
           "access-token": os.getenv("DHAN_API_KEY", ""),
           "Accept": "application/json",
           "Content-Type": "application/json"
       }
       params = {
           "symbol": symbol,
           "segment": "NSE_EQ"
       }
   ```

2. **Fallback Strategy**
   - Primary: DhanHQ API
   - Secondary: NSE API
   - Tertiary: Alternative sources

## 🔧 **Required Setup**

### **1. Static IP (For Trading APIs)**
```bash
# Set static IP for your account
curl --request POST \
--url https://api.dhan.co/v2/ip/setIP \
--header 'access-token: {Access Token}' \
--data '{
    "dhanClientId": "1000000001",
    "ip": "your_static_ip",
    "ipFlag": "PRIMARY"
}'
```

### **2. TOTP Setup (Optional)**
1. Go to **Dhan Web** → **DhanHQ Trading APIs** → **Setup TOTP**
2. Scan QR code with authenticator app
3. Confirm with first TOTP code

### **3. User Profile Validation**
```bash
curl --location 'https://api.dhan.co/v2/profile' \
--header 'access-token: {your_token}'
```

## 📊 **Data Structures**

### **Market Depth Response**
```json
{
    "type": "market_depth",
    "instrument_token": "2885633",
    "bids": [[price, quantity], ...],
    "asks": [[price, quantity], ...],
    "last_trade": {
        "price": 187.5,
        "quantity": 400,
        "side": "buy"
    }
}
```

### **Tick Data Response**
```json
{
    "type": "tick",
    "instrument_token": "2885633",
    "price": 187.5,
    "quantity": 400,
    "side": "buy",
    "timestamp": 1640995200
}
```

### **Quote Data Response**
```json
{
    "type": "quote",
    "instrument_token": "2885633",
    "ltp": 187.5,
    "change": 2.5,
    "change_percent": 1.35,
    "volume": 1000000
}
```

## 🚨 **Error Handling**

### **Common Error Types**
- `INVALID_TOKEN` - Access token expired or invalid
- `INVALID_SYMBOL` - Symbol not found
- `RATE_LIMIT` - Too many requests
- `WEBSOCKET_ERROR` - Connection issues

### **Error Response Format**
```json
{
    "type": "error",
    "code": "INVALID_TOKEN",
    "message": "Access token has expired",
    "timestamp": 1640995200
}
```

## 🔄 **Reconnection Strategy**

### **Exponential Backoff**
```python
async def handle_reconnect(self):
    if self.reconnect_attempts < self.max_reconnect_attempts:
        self.reconnect_attempts += 1
        wait_time = min(2 ** self.reconnect_attempts, 30)
        await asyncio.sleep(wait_time)
        await self.connect()
```

### **Connection Health**
- **Ping interval**: 20 seconds
- **Ping timeout**: 10 seconds
- **Max reconnection attempts**: 5
- **Backoff strategy**: Exponential (1s, 2s, 4s, 8s, 16s, 30s)

## 📈 **Performance Optimization**

### **Caching Strategy**
- **Symbol cache**: SQLite database
- **Token validation**: Every 24 hours
- **Connection pooling**: Reuse HTTP sessions
- **Message batching**: Aggregate updates

### **Rate Limiting**
- **WebSocket**: No rate limits
- **REST API**: 100 requests/minute
- **Burst limit**: 10 requests/second

## 🎯 **Best Practices**

### **1. Authentication**
- ✅ Use access tokens (24-hour validity)
- ✅ Implement token refresh logic
- ✅ Store tokens securely
- ❌ Don't hardcode credentials

### **2. WebSocket Management**
- ✅ Handle reconnections gracefully
- ✅ Implement heartbeat/ping
- ✅ Log connection status
- ❌ Don't ignore connection errors

### **3. Data Processing**
- ✅ Validate incoming data
- ✅ Handle missing fields
- ✅ Implement error recovery
- ❌ Don't assume data structure

### **4. Security**
- ✅ Use HTTPS/WSS only
- ✅ Validate all inputs
- ✅ Implement rate limiting
- ❌ Don't expose sensitive data

## 🔗 **Useful Links**

- [DhanHQ API Documentation](https://dhanhq.co/docs/v2/)
- [Authentication Guide](https://dhanhq.co/docs/v2/authentication/)
- [WebSocket Streaming](https://dhanhq.co/docs/v2/websocket-streaming/)
- [Market Data APIs](https://dhanhq.co/docs/v2/data-apis/)
- [Trading APIs](https://dhanhq.co/docs/v2/trading-apis/)

## ✅ **Integration Checklist**

- [ ] Access token obtained and configured
- [ ] Static IP set (if using trading APIs)
- [ ] WebSocket connection established
- [ ] Market depth subscription working
- [ ] Error handling implemented
- [ ] Reconnection logic tested
- [ ] Data validation working
- [ ] Performance optimized
- [ ] Security measures in place

The Order Flow Visualizer is now fully compliant with DhanHQ API v2 specifications! 🚀
