export default function Footer() {
  return (
    <footer className="bg-dark-900 border-t border-dark-800 mt-20">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold text-primary-500 mb-4">MEMAX</h3>
            <p className="text-gray-400 text-sm">
              AI-Powered OTT Platform with Personalized Recommendations
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Platform</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-primary-500">About Us</a></li>
              <li><a href="#" className="hover:text-primary-500">Features</a></li>
              <li><a href="#" className="hover:text-primary-500">Pricing</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-primary-500">Help Center</a></li>
              <li><a href="#" className="hover:text-primary-500">Contact</a></li>
              <li><a href="#" className="hover:text-primary-500">FAQ</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-primary-500">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-primary-500">Terms of Service</a></li>
              <li><a href="#" className="hover:text-primary-500">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-dark-800 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>&copy; 2026 MEMAX. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
