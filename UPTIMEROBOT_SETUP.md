# ⏰ UptimeRobot Setup - Keep Your Service Alive

## Why UptimeRobot?

Render Free Tier **spins down your service after 15 minutes of inactivity**. This means:
- First request after spin-down takes ~30 seconds (cold start)
- Could fail hackathon testing if service is down
- **Solution**: UptimeRobot pings your service every 5 minutes to keep it alive

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Create Account

1. Go to: https://uptimerobot.com
2. Click **"Sign Up Free"**
3. Enter your email and create password
4. Verify your email

**Free Plan Includes:**
- ✅ 50 monitors
- ✅ 5-minute checks
- ✅ Unlimited email alerts
- ✅ Perfect for this hackathon!

---

### Step 2: Create Monitor

1. Log in to UptimeRobot dashboard
2. Click **"+ Add New Monitor"**
3. Fill in the details:

```
Monitor Type: HTTP(s)
Friendly Name: Scambot Honeypot
URL (or IP): https://your-service-name.onrender.com/health
Monitoring Interval: Every 5 minutes
Monitor Timeout: 30 seconds
HTTP Method: GET (HEAD)
```

**Important:**
- Use your **actual Render URL** (e.g., `https://scambot-honeypot.onrender.com/health`)
- Must include `/health` at the end
- Don't add the `/api/v1/conversation` endpoint - use `/health`

4. Click **"Create Monitor"**

---

### Step 3: Verify It's Working

1. Wait 1-2 minutes
2. Check your UptimeRobot dashboard
3. Monitor should show **"Up"** status with green checkmark
4. Response time should be visible (typically 100-500ms)

**✅ Done! Your service will now stay alive 24/7**

---

## 📊 What You'll See

### Dashboard Status:

```
Status: Up (Green)
Response Time: 234 ms
Uptime Ratio: 100%
Last Check: 2 minutes ago
```

### Monitor Details:

- **Total Checks**: Increases over time
- **Up Events**: Should stay at 1 (service stayed up)
- **Down Events**: Should be 0
- **Average Response Time**: Typically 100-500ms

---

## 🔔 Optional: Set Up Alerts

Get notified if your service goes down:

1. Go to your monitor settings
2. Click **"Alert Contacts"**
3. Add your email
4. Enable alerts for:
   - ✅ When monitor goes DOWN
   - ✅ When monitor comes back UP

---

## 🧪 Testing Your Monitor

### Test 1: Check Response Time

Your monitor should show response times of **100-500ms**.

If response time is:
- ✅ 100-500ms: Perfect, service is responsive
- ⚠️ 500-2000ms: Service might be under load
- ❌ >2000ms or timeout: Service might have issues

### Test 2: Force a Check

1. Click on your monitor
2. Click **"Force Check"** button
3. Wait a few seconds
4. Status should update

### Test 3: Check Service Manually

Open your browser:
```
https://your-service-name.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "scambot-honeypot",
  "active_sessions": 0
}
```

---

## ⚠️ Troubleshooting

### Issue: Monitor shows "Down"

**Possible Causes:**
1. Render service is deploying (wait 2-5 minutes)
2. Wrong URL (check it matches your Render URL)
3. Service has crashed (check Render logs)

**Solution:**
1. Check Render dashboard - is service running?
2. Verify URL includes `/health` endpoint
3. Try accessing URL in browser
4. Check Render logs for errors

### Issue: Monitor shows "Timeout"

**Solution:**
1. Increase timeout to 60 seconds in monitor settings
2. Check if service is cold-starting (first request after sleep)
3. Verify service is running in Render dashboard

### Issue: High Response Times (>2000ms)

**Solution:**
1. Check Render service metrics
2. Verify OpenAI API is responding
3. Check for any errors in Render logs
4. May be normal for cold starts

### Issue: Monitor works but service still spins down

**Possible Causes:**
1. Monitor interval too long (should be 5 minutes)
2. Monitor disabled or paused
3. Alert contact verification pending

**Solution:**
1. Set interval to 5 minutes (free tier minimum)
2. Ensure monitor is enabled
3. Verify your email and re-enable alerts

---

## 📈 Understanding Uptime

### Uptime Ratio Explained:

- **100%**: Perfect! Service never went down
- **99%**: Service was down for ~7 minutes in last 24 hours
- **95%**: Service was down for ~1 hour in last 24 hours
- **<90%**: Major issues, investigate immediately

### Response Time Explained:

- **<200ms**: Excellent
- **200-500ms**: Good
- **500-1000ms**: Acceptable
- **1000-2000ms**: Slow, investigate
- **>2000ms**: Very slow or timing out

---

## 🎯 Best Practices

### 1. Monitor the Health Endpoint
✅ **Do**: Monitor `/health`
❌ **Don't**: Monitor `/api/v1/conversation` (requires authentication)

### 2. Use 5-Minute Intervals
- Free tier allows minimum 5-minute checks
- Perfect balance between keeping service alive and not overloading

### 3. Set Up Email Alerts
- Get notified immediately if service goes down
- Can fix issues before hackathon evaluation

### 4. Check Logs Regularly
- UptimeRobot dashboard shows historical data
- Monitor trends in response time

### 5. Test Before Submission
- Ensure monitor is active
- Verify service stays up
- Check response times are consistent

---

## 📊 Monitor Settings Reference

**Recommended Settings:**

```
Monitor Type: HTTP(s)
URL: https://your-service-name.onrender.com/health
Interval: Every 5 minutes
Timeout: 30 seconds (increase to 60 if needed)
HTTP Method: GET
HTTP Status Code: 200
```

**Optional Advanced Settings:**

```
Custom HTTP Headers: None needed
Custom POST/PUT Body: Not applicable
Alert When: Down
Alert Contacts: Your email
```

---

## 🔍 Monitoring During Hackathon

### Before Evaluation:
1. Check monitor shows "Up"
2. Verify response times are normal
3. Test the API endpoint manually
4. Ensure UptimeRobot hasn't paused the monitor

### During Evaluation:
1. Keep UptimeRobot dashboard open
2. Watch for any down events
3. Monitor response times
4. Check Render logs if issues occur

### After Evaluation:
1. Review uptime percentage
2. Check if there were any down events
3. Analyze response time trends

---

## 💡 Pro Tips

1. **Bookmark Your Monitor**: Quick access to status
2. **Enable Mobile Notifications**: Get alerts on your phone
3. **Check Before Demo**: Ensure service is up before showing anyone
4. **Monitor Multiple Endpoints**: Add `/` root endpoint as backup
5. **Set Response Time Alerts**: Get notified if service is slow

---

## 🎉 Success Criteria

Your monitor is properly set up when:

- ✅ Status shows "Up" continuously
- ✅ Response times are consistent (100-500ms)
- ✅ Uptime ratio is 100% or near 100%
- ✅ No down events in the last 24 hours
- ✅ Monitor has been checking for at least 1 hour
- ✅ Email alerts are configured
- ✅ Service accessible from browser

---

## 📞 Support

- **UptimeRobot Docs**: https://uptimerobot.com/help
- **UptimeRobot Forum**: https://uptimerobot.com/forum
- **UptimeRobot Support**: support@uptimerobot.com

---

## Quick Reference Card

```
┌─────────────────────────────────────────────┐
│         UptimeRobot Quick Setup             │
├─────────────────────────────────────────────┤
│ Monitor Type: HTTP(s)                       │
│ URL: https://YOUR-SERVICE.onrender.com/health│
│ Interval: 5 minutes                         │
│ Timeout: 30 seconds                         │
│ Method: GET                                 │
│ Expected Status: 200 OK                     │
└─────────────────────────────────────────────┘

✅ Your service will ping every 5 minutes
✅ Render won't spin down your service
✅ You'll be notified if service goes down
```

---

**Your service is now monitored and will stay alive 24/7! 🎉**
