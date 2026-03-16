import Link from 'next/link';

const Footer = () => {
    return (
        <footer className="bg-dark-200 text-gray-400 py-12 mt-20 border-t border-dark-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                    <div>
                        <h3 className="text-white font-bold mb-4">Company</h3>
                        <ul className="space-y-2">
                            <li><Link href="/about" className="hover:text-primary-400 transition-colors">About Us</Link></li>
                            <li><Link href="/jobs" className="hover:text-primary-400 transition-colors">Jobs</Link></li>
                            <li><Link href="/press" className="hover:text-primary-400 transition-colors">Press</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="text-white font-bold mb-4">Support</h3>
                        <ul className="space-y-2">
                            <li><Link href="/help" className="hover:text-primary-400 transition-colors">Help Center</Link></li>
                            <li><Link href="/terms" className="hover:text-primary-400 transition-colors">Terms of Use</Link></li>
                            <li><Link href="/privacy" className="hover:text-primary-400 transition-colors">Privacy</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="text-white font-bold mb-4">Connect</h3>
                        <ul className="space-y-2">
                            <li><a href="#" className="hover:text-primary-400 transition-colors">Facebook</a></li>
                            <li><a href="#" className="hover:text-primary-400 transition-colors">Twitter</a></li>
                            <li><a href="#" className="hover:text-primary-400 transition-colors">Instagram</a></li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="text-white font-bold mb-4">Get the App</h3>
                        <p className="text-sm mb-4">Available on iOS and Android</p>
                        <div className="flex gap-2">
                            <button className="bg-black border border-gray-600 rounded px-3 py-1 text-xs hover:border-white transition-colors">App Store</button>
                            <button className="bg-black border border-gray-600 rounded px-3 py-1 text-xs hover:border-white transition-colors">Google Play</button>
                        </div>
                    </div>
                </div>
                <div className="mt-12 pt-8 border-t border-dark-300 text-center text-sm">
                    <p>&copy; 2026 MEMAX OTT. All rights reserved.</p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
