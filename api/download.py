export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    let { url } = req.body;

    if (!url) {
        return res.status(400).json({ error: 'الرابط مطلوب' });
    }

    // تنظيف الرابط من أي شرطات زائفة بالبداية
    url = url.trim().replace(/^\/+/, '');

    try {
        const tikwmResponse = await fetch('https://www.tikwm.com/api/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ url: url })
        });
        
        const tikwmData = await tikwmResponse.json();

        if (tikwmData.code !== 0) {
            return res.status(400).json({ error: 'فشل جلب الفيديو، تأكد من الرابط.' });
        }

        return res.status(200).json({
            success: true,
            title: tikwmData.data.title || 'فيديو تيك توك',
            cover: tikwmData.data.cover,
            videoUrl: tikwmData.data.play,
            musicUrl: tikwmData.data.music
        });

    } catch (error) {
        console.error("Error:", error);
        return res.status(500).json({ error: 'حدث خطأ في الاتصال' });
    }
}
